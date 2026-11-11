(function (root) {
  'use strict';
  function residual(recall, transfer, persistent, k) {
    const m = 1 - recall * transfer;
    const b = persistent * m;
    if (k === 0) return 1;
    if (b >= 1) return 1;
    return b + (1 - b) * Math.pow((m - b) / (1 - b), k);
  }
  function cost(k, checkpoint, fpr, review, setup, volume) {
    return setup / volume + k * (checkpoint + fpr * review);
  }
  function required(recall, transfer, persistent, target, maxChecks) {
    for (let k = 1; k <= maxChecks; k++) {
      if (residual(recall, transfer, persistent, k) <= target) return k;
    }
    return null;
  }
  const api = {residual, cost, required};
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.InterpretabilityModel = api;
})(typeof window === 'undefined' ? globalThis : window);
