/**
 * Fungsi untuk memunculkan Sidebar & Topbar Mobile otomatis dengan Role-Based Access Control (RBAC)
 * Cara pakai di HTML: renderSidebar('pembayaran');
 */
function renderSidebar(activeMenu = 'dashboard') {
  // Ambil data role pengguna dari localStorage (admin / pemilik / tutor)
  const role = (localStorage.getItem('optimatika_role') || 'admin').toLowerCase();
  const userName = localStorage.getItem('optimatika_label') || (role === 'pemilik' ? 'Pemilik (Owner)' : (role === 'tutor' ? 'Tutor Pengajar' : 'Administrator'));

  // Route Guard: Proteksi akses halaman berdasarkan hak akses
  if (role === 'pemilik' && activeMenu !== 'dashboard') {
    alert('Akses Dibatasi: Akun Pemilik hanya memiliki hak akses ke Dashboard.');
    window.location.href = 'dashboard.html';
    return;
  }
  if (role === 'tutor' && activeMenu !== 'jadwal') {
    alert('Akses Dibatasi: Akun Tutor hanya memiliki hak akses ke Jadwal Belajar.');
    window.location.href = 'jadwal.html';
    return;
  }

  // Daftar semua menu dan link halamannya
  const allMenuList = [
    { id: 'dashboard', label: 'Dashboard', link: 'dashboard.html' },
    { id: 'siswa', label: 'Siswa dan Wali', link: 'siswa.html' },
    { id: 'program', label: 'Program', link: 'program.html' },
    { id: 'tutor', label: 'Tutor', link: 'tutor.html' },
    { id: 'ruang', label: 'Ruang Belajar', link: 'ruang_belajar.html' },
    { id: 'kelompok', label: 'Kelompok Belajar', link: 'kelompok_belajar.html' },
    { id: 'jadwal', label: 'Jadwal', link: 'jadwal.html' },
    { id: 'tagihan', label: 'Tagihan', link: 'tagihan.html' },
    { id: 'pembayaran', label: 'Pembayaran', link: 'pembayaran.html' }
  ];

  // Filter menu sesuai hak akses
  let menuList = allMenuList;
  let brandSub = '· Admin';

  if (role === 'pemilik') {
    menuList = allMenuList.filter(item => item.id === 'dashboard');
    brandSub = '· Pemilik';
  } else if (role === 'tutor') {
    menuList = allMenuList.filter(item => item.id === 'jadwal');
    brandSub = '· Tutor';
  }

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
        Optimatika <span class="brand-sub">${brandSub}</span>
      </div>
      <button class="mobile-menu-btn" id="mobileMenuToggle">
        <i class="bi bi-list"></i>
      </button>
    </div>

    <!-- Sidebar Menu Utama -->
    <aside class="sidebar-wrapper" id="sidebar">
      <div class="brand-container d-none d-lg-block">
        <div class="brand-title">
          Optimatika <span class="brand-sub">${brandSub}</span>
        </div>
        <div style="font-size: 11.5px; color: #8ea3c7; margin-top: 4px; padding-left: 2px;">
          Masuk: <strong style="color: #ffffff;">${userName}</strong>
        </div>
      </div>

      <nav class="sidebar-nav">
        ${menuHtml}
      </nav>

      <div class="sidebar-footer">
        <a href="javascript:void(0)" class="btn-logout" onclick="handleLogout()">
          <i class="bi bi-box-arrow-left me-2"></i>
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

/**
 * Handler logout untuk kembali ke halaman login (index.html)
 */
function handleLogout() {
  if (confirm('Apakah Anda yakin ingin keluar dari sistem Optimatika?')) {
    localStorage.removeItem('optimatika_admin_user');
    localStorage.removeItem('optimatika_role');
    localStorage.removeItem('optimatika_label');
    window.location.href = 'index.html';
  }
}