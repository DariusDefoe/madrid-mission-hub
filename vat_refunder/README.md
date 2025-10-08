# 🧾 VAT Refunder

**VAT Refunder** is a lightweight desktop application built with **Python, Tkinter, and MySQL (Dockerized)**.  
It helps manage and report VAT-refund workflows such as invoice tracking, voucher creation, and quarterly reporting.  
The app was designed for administrative environments that need clear, auditable data entry and automated report generation.

---

## 🚀 Features
- GUI data entry for Chancery and Residence invoices and vouchers  
- One-click generation of PDF and CSV reports (using ReportLab)  
- Dockerized MySQL 9.3 backend for easy setup and persistence  
- Cross-platform launcher (`start.sh`) that auto-creates a Python virtual environment  
- CSV exports automatically saved to `~/Desktop/exports`

---

## 🧩 Requirements
- Docker + Docker Compose plugin  
- Python ≥ 3.10  
- Linux or macOS (tested on Fedora 42)

---

## ⚙️ Installation & Setup
```bash
# Clone the repository
https://github.com/DariusDefoe/madrid-mission-hub.git
cd madrid-mission-hub/vat_refunder

# Copy example environment file
cp .env.example .env
# (optional) edit .env to adjust passwords or DB name

# Install necessary utilities
chmod +x setup.sh
./setup.sh

# Start MySQL + GUI
chmod +x start.sh
./start.sh
