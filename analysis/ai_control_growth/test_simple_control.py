import copy
import math
import unittest

import numpy as np
from scipy.special import expit
from scipy.integrate import quad
from scipy.stats import norm

import simple_control as simple


def example_rows():
    return [dict(id=f'{p}-{j}', protocol=p, study='one', attacker=f'attacker-{j}', monitor='monitor',
                 ln_attacker=math.log(r), ln_monitor=0., logit_sd=.6,
                 value=float(expit(a-.8*math.log(r))))
            for p,a in [('a',1.2),('b',2.4)] for j,r in enumerate([.5,1.,2.,4.])]


class SimpleModelChecks(unittest.TestCase):
    def test_posterior_against_independent_gaussian_rejection(self):
        rows=example_rows()
        x=np.array([[-o['ln_attacker'],float(o['protocol']=='a'),float(o['protocol']=='b')] for o in rows])
        y=np.array([math.log(o['value']/(1-o['value'])) for o in rows])
        prior=np.diag([1/.8**2,1/4**2,1/4**2])
        covariance=np.linalg.inv(x.T@x/.6**2+prior)
        mean=covariance@(x.T@y/.6**2+prior@np.array([.6,0,0]))
        reference=np.random.default_rng(91).multivariate_normal(mean,covariance,size=200000)
        reference=reference[reference[:,0]>=0]
        sampled=simple.posterior(rows,['a','b'],draws=2000,burn=500).reshape(-1,3)
        np.testing.assert_allclose(sampled.mean(axis=0),reference.mean(axis=0),atol=.04)
        np.testing.assert_allclose(np.quantile(sampled,[.05,.95],axis=0),np.quantile(reference,[.05,.95],axis=0),atol=.06)

    def test_log_free_safety_identity_and_monotonicity(self):
        r=np.array([.1,1,4,20,100])
        a,k=2.3,1.4
        r50=math.exp(a/k)
        np.testing.assert_allclose(1/(1+(r/r50)**k),expit(a-k*np.log(r)))
        self.assertTrue(np.all(np.diff(1/(1+(r/r50)**k))<0))

    def test_factoring_protocol_strength_collapses_curves(self):
        ratios=np.geomspace(.001,1000,101)
        for slope in [.7,1.2,2.]:
            for intercept in [-2.,0.,2.,5.]:
                r50=math.exp(intercept/slope)
                normalized=ratios/r50
                collapsed=normalized**slope/(1+normalized**slope)
                original=expit(slope*np.log(ratios)-intercept)
                np.testing.assert_allclose(collapsed,original,atol=1e-14)
                self.assertAlmostEqual((r50/r50)**slope/(1+(r50/r50)**slope),.5)

    def test_timeline_horizon_inverts_failure_model(self):
        for intercept in [-1.,2.,5.]:
            for slope in [.7,1.2,2.]:
                for ceiling in [.01,.05,.2,.5]:
                    ratio=math.exp((intercept+math.log(ceiling/(1-ceiling)))/slope)
                    for monitor in [.1,1.,10.]:
                        attacker=monitor*ratio
                        failure=expit(slope*math.log(attacker/monitor)-intercept)
                        self.assertAlmostEqual(failure,ceiling)

    def test_censored_posterior_against_quadrature(self):
        threshold=math.log(.8/.2)
        density=lambda a:norm.pdf(a,scale=4)*norm.cdf((a-threshold)/.5)
        normalization=quad(density,-30,30)[0]
        expected=quad(lambda a:a*density(a),-30,30)[0]/normalization
        rows=[dict(protocol='a',ln_attacker=0.,ln_monitor=0.,logit_sd=.5,lower=.8)]
        draws=simple.posterior(rows,['a'],draws=2000,burn=500).reshape(-1,2)
        self.assertLess(abs(draws[:,1].mean()-expected),.1)

    def test_no_hidden_time_or_source_terms(self):
        rows=example_rows();changed=copy.deepcopy(rows)
        for i,o in enumerate(changed):
            o.update(study=f'different-{i}',year=1000*i,date='2099-01-01',metric='different event definition')
        np.testing.assert_array_equal(simple.posterior(rows,['a','b'],draws=30,burn=10,chains=2),
                                      simple.posterior(changed,['a','b'],draws=30,burn=10,chains=2))


if __name__=='__main__':unittest.main()
