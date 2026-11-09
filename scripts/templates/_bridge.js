/* Talks to the book page that embeds this widget (see includes/explorer-embed.html). */
(function () {
  function sendHeight() {
    var h = Math.ceil(document.documentElement.getBoundingClientRect().height);
    parent.postMessage({ type: 'explorer-height', height: h }, '*');
  }
  window.addEventListener('message', function (e) {
    if (e.data && e.data.type === 'explorer-theme') {
      document.documentElement.setAttribute('data-theme', e.data.dark ? 'dark' : 'light');
    }
  });
  if (window.ResizeObserver) new ResizeObserver(sendHeight).observe(document.body);
  window.addEventListener('load', function () { sendHeight(); parent.postMessage({ type: 'explorer-ready' }, '*'); });
})();
