const {test} = require('node:test');
const assert = require('node:assert/strict');
const {residual, cost, required} = require('../../interpretability_model.js');
test('one checkpoint reproduces the transferred observation for all dependence settings', () => {
  for (const r of [0, .05, .43, .73, .96, 1]) for (const t of [0, .8, 1]) for (const z of [0, .3, 1]) {
    assert.ok(Math.abs(residual(r,t,z,1)-(1-r*t)) < 1e-12);
  }
});
test('independent repetitions, persistent errors, and endpoint cases', () => {
  assert.ok(Math.abs(residual(.73,1,0,6)-.27**6) < 1e-12);
  assert.ok(Math.abs(residual(.73,1,1,20)-.27) < 1e-12);
  assert.equal(residual(0,1,1,20),1);
  assert.equal(residual(1,1,1,1),0);
  assert.equal(required(.73,1,0,.001,20),6);
  assert.equal(required(.73,1,.01,.001,20),null);
});
test('more checkpoints never increase misses; persistence never improves detection', () => {
  for (const r of [.05,.43,.73,.96]) for (const z of [0,.1,.5,1]) for(let k=2;k<=20;k++) {
    assert.ok(residual(r,1,z,k) <= residual(r,1,z,k-1)+1e-12);
    assert.ok(residual(r,1,z,k) >= residual(r,1,0,k)-1e-12);
  }
});
test('cost includes setup, all checks and expected false-alarm handling', () => {
  assert.equal(cost(6,.001,.01,1,100,10000),.076);
});
