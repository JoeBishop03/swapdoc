// "Privacy settings" links reopen Google's consent message, so visitors can change
// their advertising choice at any time.
(function () {
  function openSettings(e) {
    e.preventDefault();
    window.googlefc = window.googlefc || {};
    window.googlefc.callbackQueue = window.googlefc.callbackQueue || [];
    window.googlefc.callbackQueue.push({
      'CONSENT_API_READY': function () { window.googlefc.showRevocationMessage(); }
    });
  }
  document.querySelectorAll('#privacy-settings, .js-privacy-settings').forEach(function (a) {
    a.addEventListener('click', openSettings);
  });
})();
