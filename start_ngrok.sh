#!/bin/bash

# Kiểm tra xem ngrok đã được cấu hình chưa
if ! ngrok config check > /dev/null 2>&1; then
    echo "==================================================================="
    echo "LỖI: Ngrok chưa được cấu hình với authtoken."
    echo "Vui lòng thực hiện các bước sau:"
    echo "1. Đăng ký tài khoản tại: https://dashboard.ngrok.com/signup"
    echo "2. Lấy authtoken từ: https://dashboard.ngrok.com/get-started/your-authtoken"
    echo "3. Cấu hình ngrok với lệnh: ngrok config add-authtoken YOUR_AUTH_TOKEN"
    echo "==================================================================="
    exit 1
fi

# Tạo tunnel ngrok đến máy chủ mem0-mcp
echo "Tạo tunnel ngrok đến http://localhost:8080..."
ngrok http 8080
