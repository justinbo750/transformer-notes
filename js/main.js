/* Transformer 拆解笔记 — 页面交互：滚动进度、章节高亮、代码复制、渐入动画 */
(function () {
  const bar = document.getElementById('progress');

  /* ---------------------------------------------------------- 滚动进度 */
  function onScroll() {
    const doc = document.documentElement;
    const max = doc.scrollHeight - doc.clientHeight;
    const ratio = max > 0 ? doc.scrollTop / max : 0;
    bar.style.width = (ratio * 100).toFixed(2) + '%';
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  /* ---------------------------------------------------------- 章节高亮 */
  const links = Array.from(document.querySelectorAll('.nav-links a'));
  const sections = links
    .map(a => document.querySelector(a.getAttribute('href')))
    .filter(Boolean);

  function setActive() {
    const mid = window.scrollY + window.innerHeight * 0.32;
    let current = null;
    for (const s of sections) {
      if (s.offsetTop <= mid) current = s;
    }
    links.forEach(a => {
      const on = current && a.getAttribute('href') === '#' + current.id;
      a.classList.toggle('active', !!on);
      if (on) {
        // 让当前项滚动到导航可视区
        const box = a.parentElement;
        const need = a.offsetLeft - box.clientWidth / 2 + a.offsetWidth / 2;
        if (Math.abs(box.scrollLeft - need) > 40) {
          box.scrollTo({ left: need, behavior: 'smooth' });
        }
      }
    });
  }
  window.addEventListener('scroll', setActive, { passive: true });
  setActive();

  /* ---------------------------------------------------------- 代码复制 */
  document.querySelectorAll('.code .copy').forEach(btn => {
    btn.addEventListener('click', () => {
      const pre = btn.closest('.code').querySelector('pre');
      const clone = pre.cloneNode(true);
      clone.querySelectorAll('.ln').forEach(el => el.remove());
      const text = clone.textContent.replace(/\u00a0/g, ' ');
      const done = () => {
        const old = btn.textContent;
        btn.textContent = '已复制';
        setTimeout(() => { btn.textContent = old; }, 1400);
      };
      if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(done).catch(done);
      } else {
        const ta = document.createElement('textarea');
        ta.value = text;
        ta.style.position = 'fixed';
        ta.style.opacity = '0';
        document.body.appendChild(ta);
        ta.select();
        try { document.execCommand('copy'); } catch (e) { /* 忽略 */ }
        document.body.removeChild(ta);
        done();
      }
    });
  });

  /* ---------------------------------------------------------- 渐入 */
  const items = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach(en => {
        if (en.isIntersecting) {
          en.target.classList.add('in');
          io.unobserve(en.target);
        }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.06 });
    items.forEach(el => io.observe(el));
  } else {
    items.forEach(el => el.classList.add('in'));
  }
})();
