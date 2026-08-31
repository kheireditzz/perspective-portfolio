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
    photo: "profile.jpg",
    logo: "profile.jpg",
    bio: "Selamat datang di portofolio digital Miftahul Khairin. Mengembangkan aplikasi full-stack berskala besar, sistem otomatisasi cerdas, bot AI, dan antarmuka spasial modern dengan performa tinggi 120 FPS.",
    
    // Toko Digital Resmi
    storeUrl: "https://produk.kheireditz.my.id",

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
      title: "Next.js 15, Python, Supabase & Go",
      desc: "Aplikasi web full-stack, cloud serverless API, database PostgreSQL & performa ultra cepat."
    },
    asset: {
      badge: "TOKO DIGITAL RESMI",
      title: "Kheireditz Produk Digital",
      desc: "Kunjungi portal resmi: https://produk.kheireditz.my.id dengan sistem QRIS otomatis.",
      url: "https://produk.kheireditz.my.id"
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
      category: "01 / PLATFORM TOKO DIGITAL & SAAS",
      title: "Kheireditz Produk — Official Store",
      desc: "Toko produk digital full-stack dengan integrasi database Supabase Cloud, pembayaran QRIS otomatis, penerbitan lisensi instan, dan riwayat transaksi realtime.",
      tech: "Python MVC • Supabase PostgreSQL • Tailwind CSS • Vercel",
      link: "https://produk.kheireditz.my.id",
      githubUrl: "https://github.com/kheireditzz/digital-product-store",
      icon: "shopping-bag"
    },
    {
      id: 2,
      category: "02 / APLIKASI WEB ENTERPRISE",
      title: "Sistem Manajemen Gudang & Logistik",
      desc: "Platform manajemen inventaris multi-cabang dengan analitik realtime, cetak barcode otomatis, dan sinkronisasi cloud terpusat.",
      tech: "Next.js 14 • Node.js • PostgreSQL • Docker",
      link: "https://github.com/kheireditzz",
      githubUrl: "https://github.com/kheireditzz/warehouse-management",
      icon: "layers"
    },
    {
      id: 3,
      category: "03 / OTOMASI & BOT CERDAS",
      title: "TikTok Affiliate Auto-Uploader Suite",
      desc: "Script otomasi Python untuk mengunduh, mengedit, menambahkan audio tren, dan mengunggah video affiliasi otomatis tanpa watermark.",
      tech: "Python • FFmpeg • Selenium • Termux Linux",
      link: "https://produk.kheireditz.my.id",
      githubUrl: "https://github.com/kheireditzz/tiktok-auto-uploader",
      icon: "cpu"
    },
    {
      id: 4,
      category: "04 / CLOUD MICROSERVICES & API",
      title: "High-Performance WhatsApp Gateway API",
      desc: "RESTful API multi-device dengan protokol Baileys, mendukung webhook pesan masuk, pengiriman massal, dan integrasi AI pintar.",
      tech: "Node.js • Express • Redis • WebSocket",
      link: "https://github.com/kheireditzz",
      githubUrl: "https://github.com/kheireditzz/whatsapp-gateway-api",
      icon: "activity"
    },
    {
      id: 5,
      category: "05 / ANTARMUKA SPASIAL & 3D WEB",
      title: "Perspective 3D Spatial Portfolio Engine",
      desc: "Engine antarmuka web modern dengan simulasi pencahayaan volumetric, kartu kanvas kedalaman multi-layer, dan fluid dynamic motion.",
      tech: "Tailwind CSS • Vanilla JS • CSS 3D Transforms",
      link: "https://portofolio.kheireditz.my.id",
      githubUrl: "https://github.com/kheireditzz/perspective-portfolio",
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
      badge: "FULL-STACK SAAS",
      title: "OmniAI Multi-Model SaaS Platform",
      desc: "Platform SaaS multi-AI (GPT-4o, Claude, Gemini, DeepSeek) dengan sistem pembayaran otomatis QRIS & lisensi komersial lifetime.",
      price: "Rp 149.000",
      originalPrice: "Rp 499.000",
      demoUrl: "https://produk.kheireditz.my.id",
      features: [
        "Full-Stack Next.js 15 + FastAPI Python",
        "Integrasi Supabase Cloud PostgreSQL",
        "Pembayaran QRIS & Lisensi Otomatis"
      ]
    },
    {
      id: 2,
      badge: "DASHBOARD UI",
      title: "Next.js 15 Tailwind UI Dashboard Kit",
      desc: "Koleksi 45+ modul antarmuka dashboard analitik, billing panel, charts dan manajemen pengguna dengan tema dark mode Obsidian & Orange.",
      price: "Rp 119.000",
      originalPrice: "Rp 399.000",
      demoUrl: "https://produk.kheireditz.my.id",
      features: [
        "45+ Komponen Reusable & Responsive",
        "Charts Interaktif Recharts & Lucide Icons",
        "Desain Ultra Modern 120 FPS"
      ]
    },
    {
      id: 3,
      badge: "BOT OTOMASI",
      title: "TikTok Affiliate Smart Uploader Suite",
      desc: "Script Python otomatisasi upload video affiliasi, AI caption generator, pemilihan audio tren, dan anti-deteksi headless.",
      price: "Rp 99.000",
      originalPrice: "Rp 349.000",
      demoUrl: "https://produk.kheireditz.my.id",
      features: [
        "Script Python Otomasi Termux & VPS",
        "Bypass Headless & Multi-Akun",
        "Panduan Setup Lengkap & Lifetime Update"
      ]
    }
  ]
};
