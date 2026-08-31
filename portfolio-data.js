/**
 * =========================================================================
 * KONFIGURASI LENGKAP & PUSAT DATA PORTOFOLIO MIFTAHUL KHAIRIN
 * =========================================================================
 * Di file ini Anda bisa mengatur SEMUA data website secara lengkap:
 * - Identitas Diri, Foto, Kontak, CV/Resume, & Media Sosial
 * - 3 Kartu Layanan Spasial 3D
 * - Portofolio Proyek Lengkap (Judul, Kategori, Deskripsi, Tech, URL Demo & GitHub)
 * - Galeri Foto Dokumentasi Lengkap (URL Gambar, Tag/Label, Deskripsi)
 * - Video Showcase YouTube (Judul, Deskripsi, Embed URL, Link Nonton Langsung)
 * - Produk Toko Digital (Judul, Harga, Badge, Deskripsi, Fitur, Link Beli WA & Demo URL)
 * - Riwayat Pengalaman Kerja / Karir & Skill Badges
 */

window.PORTFOLIO_CONFIG = {
  // =========================================================================
  // 1. INFORMASI PROFIL, IDENTITAS, KONTAK & MEDIA SOSIAL
  // =========================================================================
  profile: {
    name: "MIFTAHUL KHAIRIN",
    profession: "Full-Stack Developer & Kreator Digital",
    location: "Indonesia • Siap Kerja Jarak Jauh (Remote)",
    status: "Tersedia untuk Proyek Baru & Konsultasi",
    photo: "https://i.ibb.co.com/840ySX1j/Screenshot-20260831-064748.jpg",
    logo: "https://i.ibb.co.com/840ySX1j/Screenshot-20260831-064748.jpg",
    bio: "Selamat datang di portofolio digital Miftahul Khairin. Mengembangkan aplikasi full-stack berskala besar, sistem otomatisasi cerdas, bot AI, dan antarmuka spasial modern dengan performa tinggi 120 FPS.",
    
    // Kontak & Chat Langsung
    whatsapp: "62895321154498", // Nomor WhatsApp aktif
    email: "miftahulkhairim1@gmail.com", // Alamat email resmi
    telegram: "https://t.me/miftahulkhairin",
    
    // Tautan Media Sosial & Kode
    socialLinks: {
      github: "https://github.com/kheireditzz",
      linkedin: "https://linkedin.com/in/miftahulkhairin",
      instagram: "https://www.instagram.com/khairindtz",
      youtube: "https://youtube.com/@miftahulkhairin",
      tiktok: "https://tiktok.com/@kheireditz"
    },

    // Header & Teks Tombol
    headerTitle: "Miftahul Khairin",
    headerSubtitle: "Perspective Engine",
    headerButtonText: "Hubungi Saya"
  },

  // =========================================================================
  // 2. 3 KARTU KANVAS SPASIAL 3D (DI BAWAH FOTO PROFIL)
  // =========================================================================
  cards3D: {
    skill: {
      badge: "ARSITEKTUR UTAMA",
      title: "Next.js 14, Node.js, Go & Python",
      desc: "Aplikasi web modern, API cloud microservices, caching Redis & performa ultra cepat."
    },
    asset: {
      badge: "SOLUSI DIGITAL",
      title: "Toko Digital & Script Otomasi",
      desc: "Source code enterprise, bot affiliate cerdas, automasi background & integrasi AI."
    },
    video: {
      badge: "MULTIMEDIA",
      title: "Video Demonstrasi & Showcase",
      desc: "Tonton presentasi video interaktif & demo pengujian sistem secara langsung."
    }
  },

  // =========================================================================
  // 3. DAFTAR HASIL KARYA & PROYEK (LENGKAP DENGAN URL DEMO & GITHUB)
  // =========================================================================
  projects: [
    {
      id: 1,
      category: "01 / APLIKASI WEB ENTERPRISE",
      title: "Sistem Manajemen Gudang & Logistik",
      desc: "Platform manajemen inventaris multi-cabang dengan analitik realtime, cetak barcode otomatis, dan sinkronisasi cloud terpusat.",
      tech: "Next.js 14 • Node.js • PostgreSQL • Docker",
      link: "https://github.com/miftahulkhairin", // URL Demo Web atau GitHub
      githubUrl: "https://github.com/miftahulkhairin/warehouse-management",
      icon: "layers"
    },
    {
      id: 2,
      category: "02 / OTOMASI & BOT CERDAS",
      title: "TikTok Affiliate Auto-Uploader Suite",
      desc: "Script otomasi Python untuk mengunduh, mengedit, menambahkan audio tren, dan mengunggah video affiliasi otomatis tanpa watermark.",
      tech: "Python • FFmpeg • Selenium • Termux Linux",
      link: "https://github.com/miftahulkhairin",
      githubUrl: "https://github.com/miftahulkhairin/tiktok-auto-uploader",
      icon: "cpu"
    },
    {
      id: 3,
      category: "03 / CLOUD MICROSERVICES & API",
      title: "High-Performance WhatsApp Gateway API",
      desc: "RESTful API multi-device dengan protokol Baileys, mendukung webhook pesan masuk, pengiriman massal, dan integrasi AI pintar.",
      tech: "Node.js • Express • Redis • WebSocket",
      link: "https://github.com/miftahulkhairin",
      githubUrl: "https://github.com/miftahulkhairin/whatsapp-gateway-api",
      icon: "activity"
    },
    {
      id: 4,
      category: "04 / ANTARMUKA SPASIAL & 3D WEB",
      title: "Perspective 3D Spatial Portfolio Engine",
      desc: "Engine antarmuka web modern dengan simulasi pencahayaan volumetric, kartu kanvas kedalaman multi-layer, dan fluid dynamic motion.",
      tech: "Tailwind CSS • Vanilla JS • CSS 3D Transforms",
      link: "https://github.com/miftahulkhairin",
      githubUrl: "https://github.com/miftahulkhairin/perspective-portfolio",
      icon: "box"
    }
  ],

  // =========================================================================
  // 4. DAFTAR FOTO GALERI DOKUMENTASI LENGKAP
  // =========================================================================
  gallery: [
    {
      id: 1,
      tag: "DOKUMENTASI KARYA",
      title: "Arsitektur Server & Bot Linux",
      img: "https://i.ibb.co.com/840ySX1j/Screenshot-20260831-064748.jpg",
      desc: "Konfigurasi server termux Linux dan cluster daemon background 24/7."
    },
    {
      id: 2,
      tag: "ANTARMUKA PENGGUNA",
      title: "Desain Dashboard Spasial",
      img: "https://i.ibb.co.com/840ySX1j/Screenshot-20260831-064748.jpg",
      desc: "Tampilan visual dashboard kedalaman spasial dengan render responsif."
    },
    {
      id: 3,
      tag: "SISTEM TELEMETRI",
      title: "Konsol Telemetri Cloud",
      img: "https://i.ibb.co.com/840ySX1j/Screenshot-20260831-064748.jpg",
      desc: "Monitoring metrik performa latensi endpoint API dan analitik sistem."
    },
    {
      id: 4,
      tag: "DAEMON OTOMASI",
      title: "Cluster Bot Otonom",
      img: "https://i.ibb.co.com/840ySX1j/Screenshot-20260831-064748.jpg",
      desc: "Eksekusi runtime tugas otomatisasi multi-thread dengan logging realtime."
    }
  ],

  // =========================================================================
  // 5. DAFTAR VIDEO DEMONSTRASI & SHOWCASE (YOUTUBE EMBED + URL LANGSUNG)
  // =========================================================================
  videos: [
    {
      id: 1,
      title: "Reel Demonstrasi Perspective UI Engine",
      desc: "Preview performa 120 FPS antarmuka spasial kedalaman 3D.",
      embed: "https://www.youtube-nocookie.com/embed/dQw4w9WgXcQ?controls=1&rel=0",
      videoUrl: "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    },
    {
      id: 2,
      title: "Demo Cluster Bot AI & Otomasi Cloud",
      desc: "Simulasi eksekusi daemon background 24/7 dengan soket realtime.",
      embed: "https://www.youtube-nocookie.com/embed/dQw4w9WgXcQ?controls=1&rel=0",
      videoUrl: "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    },
    {
      id: 3,
      title: "Showcase Arsitektur Web Next.js 14 Pro",
      desc: "Integrasi API microservices, database caching, dan dynamic render.",
      embed: "https://www.youtube-nocookie.com/embed/dQw4w9WgXcQ?controls=1&rel=0",
      videoUrl: "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    }
  ],

  // =========================================================================
  // 6. PRODUK TOKO DIGITAL (LENGKAP DENGAN HARGA, FITUR, DEMO & WHATSAPP)
  // =========================================================================
  products: [
    {
      id: 1,
      badge: "SOURCE CODE",
      title: "Perspective UI Pro Boilerplate",
      desc: "Template Next.js 14 + Tailwind lengkap dengan kanvas kedalaman spasial 3D, mode gelap, dan komponen modern siap pakai.",
      price: "Rp 199.000",
      originalPrice: "Rp 350.000",
      demoUrl: "https://github.com/miftahulkhairin",
      features: [
        "Kode Sumber Lengkap Next.js 14",
        "Efek Spasial 3D Continuous Carousel",
        "Gratis Update Selamanya & Panduan Setup"
      ]
    },
    {
      id: 2,
      badge: "BOT & SCRIPT",
      title: "TikTok Affiliate Smart Uploader",
      desc: "Script Python otomatisasi upload video affiliasi, pembuatan caption otomatis dengan AI, musik tren, dan anti-deteksi headless.",
      price: "Rp 299.000",
      originalPrice: "Rp 500.000",
      demoUrl: "https://github.com/miftahulkhairin",
      features: [
        "Script Python Otomasi Lengkap",
        "Bypass Headless & Multi-Akun",
        "Panduan Instalasi Termux & VPS Lengkap"
      ]
    },
    {
      id: 3,
      badge: "BOT OTOMASI",
      title: "WhatsApp AI Customer Auto-Reply",
      desc: "Bot WhatsApp Baileys otomatis merespons pesan pelanggan dengan integrasi kecerdasan buatan Gemini AI secara 24/7.",
      price: "Rp 149.000",
      originalPrice: "Rp 250.000",
      demoUrl: "https://github.com/miftahulkhairin",
      features: [
        "Kode Sumber Node.js Baileys",
        "Integrasi API Gemini AI Cerdas",
        "Multi-Device Session & Webhook Support"
      ]
    }
  ]
};
