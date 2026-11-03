/**
 * Fungsi untuk memunculkan Sidebar & Topbar Mobile otomatis
 * Cara pakai di HTML: renderSidebar('pembayaran');
 */
function renderSidebar(activeMenu = 'program') {
  // Daftar semua menu dan link halamannya
  const menuList = [
    { id: 'siswa', label: 'Siswa dan Wali', link: 'siswa.html' },
    { id: 'program', label: 'Program', link: 'program.html' },
    { id: 'tutor', label: 'Tutor', link: 'tutor.html' },
    { id: 'ruang', label: 'Ruang Belajar', link: 'ruang_belajar.html' },
    { id: 'kelompok', label: 'Kelompok Belajar', link: 'kelompok_belajar.html' },
    { id: 'jadwal', label: 'Jadwal', link: 'jadwal.html' },
    { id: 'tagihan', label: 'Tagihan', link: 'tagihan.html' },
    { id: 'pembayaran', label: 'Pembayaran', link: 'pembayaran.html' }
  ];

  // Susun tombol link menu secara dinamis
  let menuHtml = '';
  menuList.forEach(item => {
    // Beri class 'active' (pil putih) jika menunya sedang dibuka
    const activeClass = (item.id === activeMenu) ? 'active' : '';
    menuHtml += `
      <a href="${item.link}" class="nav-item-btn ${activeClass}">
        <span>${item.label}</span>
      </a>
    `;
  });

  // Template Sidebar Lengkap
  const sidebarTemplate = `
    <!-- Mobile Topbar (khusus layar HP) -->
    <div class="mobile-header d-lg-none w-100">
      <div class="brand-title">
        Optimatika <span class="brand-sub">· Admin</span>
      </div>
      <button class="mobile-menu-btn" id="mobileMenuToggle">
        <i class="bi bi-list"></i>
      </button>
    </div>

    <!-- Sidebar Menu Utama -->
    <aside class="sidebar-wrapper" id="sidebar">
      <div class="brand-container d-none d-lg-block">
        <div class="brand-title">
          Optimatika <span class="brand-sub">· Admin</span>
        </div>
      </div>

      <nav class="sidebar-nav">
        ${menuHtml}
      </nav>

      <div class="sidebar-footer">
        <a href="javascript:void(0)" class="btn-logout" onclick="alert('Keluar dari sesi admin')">
          <span>Keluar</span>
        </a>
      </div>
    </aside>
  `;

  // Masukkan template ke dalam elemen penampung di HTML
  const container = document.getElementById('sidebar-container');
  if (container) {
    container.innerHTML = sidebarTemplate;

    // Pasang tombol menu untuk mobile (responsif)
    const toggleBtn = document.getElementById('mobileMenuToggle');
    const sidebar = document.getElementById('sidebar');
    if (toggleBtn && sidebar) {
      toggleBtn.addEventListener('click', () => {
        sidebar.classList.toggle('show');
      });
    }
  }
}