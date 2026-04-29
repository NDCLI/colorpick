import React from 'react';
import { motion } from 'framer-motion';
import {
  Pipette,
  Maximize2,
  Cpu,
  Download,
  Code,
  CheckCircle2,
  Layers
} from 'lucide-react';
import './App.css';

function App() {
  const fadeIn = {
    initial: { opacity: 0, y: 20 },
    whileInView: { opacity: 1, y: 0 },
    viewport: { once: true },
    transition: { duration: 0.6 }
  };

  const handleDownloadSetup = (e: React.MouseEvent) => {
    e.preventDefault();
    const url = "https://raw.githubusercontent.com/NDCLI/colorpick/master/Setup_ColorPicker.bat";
    fetch(url)
      .then(response => response.blob())
      .then(blob => {
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = "Setup_ColorPicker.bat";
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      })
      .catch(err => {
        console.error("Lỗi khi tải file:", err);
        window.open(url, '_blank');
      });
  };

  return (
    <div className="landing-page">
      {/* Navigation */}
      <nav className="glass">
        <div className="container nav-content">
          <div className="logo">
            <span>ColorPicker <span className="v3">v3.1</span></span>
          </div>
          <div className="nav-links">
            <a href="#features">Tính năng</a>
            <a href="#ai">Engine AI</a>
            <a href="#shortcuts">Phím tắt</a>
            <a href="https://github.com/NDCLI/colorpick" target="_blank" rel="noopener noreferrer" className="btn-secondary btn-sm">
              <Code size={18} /> GitHub
            </a>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="hero">
        <div className="container">
          <motion.div
            className="hero-grid"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 1 }}
          >
            <div className="hero-text">
              <motion.div {...fadeIn} className="badge">
                Phát triển bởi Antigravity AI
              </motion.div>
              <motion.h1
                className="gradient-text"
                initial={{ opacity: 0, x: -30 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.2, duration: 0.8 }}
              >
                Color <span className="text-accent">Picker</span>
              </motion.h1>
              <motion.p
                className="hero-desc"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.4, duration: 0.8 }}
              >
                Bộ công cụ AI mạnh mẽ dành riêng cho Windows. Lấy màu chính xác đến từng pixel
                và phân tích vùng ảnh thông minh với công nghệ vượt trội.
              </motion.p>
              <motion.div
                className="hero-btns"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.6, duration: 0.8 }}
              >
                <a href="#" onClick={handleDownloadSetup} className="btn-primary">
                  <Download size={20} /> Tải xuống
                </a>
                <a href="https://github.com/NDCLI/colorpick" target="_blank" rel="noopener noreferrer" className="btn-secondary">
                  <Code size={20} /> GitHub Repo
                </a>
              </motion.div>
            </div>
            <div className="hero-visual">
              <div className="image-container glass">
                <img src="/hero.png" alt="Color Picker UI" />
                <div className="glow-effect"></div>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Product Suite */}
      <section id="features" className="suite">
        <div className="container">
          <motion.div {...fadeIn} className="section-header">
            <h2 className="gradient-text">Hệ sinh thái công cụ</h2>
            <p>Ba ứng dụng độc lập, giải quyết mọi nhu cầu về màu sắc và phân tích hình ảnh.</p>
          </motion.div>

          <div className="card-grid">
            {[
              {
                icon: <Pipette size={32} />,
                title: "Color Picker",
                desc: "Phiên bản đầy đủ kết hợp pick điểm và phân tích vùng. All-in-one cho Designer."
              },
              {
                icon: <Maximize2 size={32} />,
                title: "Color Pick",
                desc: "Chuyên biệt cho việc lấy màu điểm với kính lúp siêu nét. Nhẹ và nhanh."
              },
              {
                icon: <Layers size={32} />,
                title: "Color Analyze",
                desc: "Vẽ vùng Lasso hoặc dán từ Clipboard để AI bóc tách các nhóm màu chính."
              }
            ].map((item, index) => (
              <motion.div
                key={index}
                className="glass-card"
                whileHover={{ y: -10 }}
                {...fadeIn}
                transition={{ delay: index * 0.1 }}
              >
                <div className="card-icon">{item.icon}</div>
                <h3>{item.title}</h3>
                <p>{item.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* AI Engine Section */}
      <section id="ai" className="ai-engine glass">
        <div className="container">
          <div className="ai-content">
            <motion.div {...fadeIn} className="ai-text">
              <div className="badge">Công nghệ Ensemble Voting</div>
              <h2 className="gradient-text">Engine Phân Loại Màu 6 Lõi</h2>
              <p>
                Không chỉ là lấy mã HEX, hệ thống AI của chúng tôi sử dụng 6 thuật toán phối hợp
                để định danh màu sắc chính xác nhất.
              </p>
              <ul className="ai-list">
                <li><CheckCircle2 size={18} className="text-accent" /> <strong>Saliency Engine:</strong> Ưu tiên màu bão hòa</li>
                <li><CheckCircle2 size={18} className="text-accent" /> <strong>BG Remove:</strong> Tự động loại bỏ màu nền viền</li>
                <li><CheckCircle2 size={18} className="text-accent" /> <strong>K-Means:</strong> Phân cụm màu sắc học máy</li>
                <li><CheckCircle2 size={18} className="text-accent" /> <strong>LAB Expert:</strong> So sánh DeltaE chuẩn CIE</li>
              </ul>
            </motion.div>
            <motion.div {...fadeIn} className="ai-visual">
              <Cpu size={200} className="cpu-icon text-accent" />
            </motion.div>
          </div>
        </div>
      </section>

      {/* Shortcuts */}
      <section id="shortcuts" className="shortcuts">
        <div className="container">
          <motion.div {...fadeIn} className="section-header">
            <h2 className="gradient-text">Thao tác trong chớp mắt</h2>
            <p>Hệ thống phím tắt toàn cục giúp bạn làm việc không cần rời tay khỏi bàn phím.</p>
          </motion.div>

          <div className="shortcut-table glass">
            <div className="table-header">
              <span>Phím tắt</span>
              <span>Hành động</span>
              <span>Ứng dụng</span>
            </div>
            {[
              { key: "Alt + S", action: "Mở kính lúp pick điểm màu", app: "Color Picker / Pick" },
              { key: "Alt + A", action: "Vẽ vùng Lasso phân tích", app: "Color Picker / Analyze" },
              { key: "Ctrl + V", action: "Phân tích ảnh Clipboard", app: "Color Analyze" },
              { key: "Esc", action: "Đóng / Hủy thao tác", app: "Tất cả" },
            ].map((item, i) => (
              <div key={i} className="table-row">
                <span className="key-code">{item.key}</span>
                <span>{item.action}</span>
                <span className="app-tag">{item.app}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Download */}
      <section id="download" className="cta">
        <div className="container">
          <motion.div className="cta-box glass" {...fadeIn}>
            <h2>Sẵn sàng trải nghiệm?</h2>
            <p>Tải xuống bản cài đặt tự động và bắt đầu nâng tầm quy trình làm việc của bạn.</p>
            <div className="install-steps">
              <div className="step">
                <span className="step-num">1</span>
                <span>Tải file Setup (.BAT)</span>
              </div>
              <div className="step">
                <span className="step-num">2</span>
                <span>Chạy để tự động cài đặt</span>
              </div>
              <div className="step">
                <span className="step-num">3</span>
                <span>Bắt đầu lấy màu</span>
              </div>
            </div>
            <div className="hero-btns center">
              <a href="#" onClick={handleDownloadSetup} className="btn-primary">
                <Download size={20} /> Tải xuống
              </a>
              <a href="https://github.com/NDCLI/colorpick" target="_blank" rel="noopener noreferrer" className="btn-secondary">
                <Code size={20} /> GitHub Repo
              </a>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer>
        <div className="container">
          <div className="footer-content">
            <div className="footer-info">
              <h3>ColorPicker</h3>
              <p>Tiện ích mã nguồn mở cho cộng đồng Windows.</p>
            </div>
            <div className="footer-links">
              <a href="#">Bảo mật</a>
              <a href="#">Điều khoản</a>
              <a href="#">Liên hệ</a>
            </div>
          </div>
          <div className="footer-bottom">
            <p>© 2026 Color Picker Suite. Licensed under MIT.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
