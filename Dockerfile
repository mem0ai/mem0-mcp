FROM python:3.12-slim

WORKDIR /app

# Cài đặt các dependency hệ thống
RUN apt-get update && \
    apt-get install -y wget unzip curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Cài đặt uv
RUN pip install --upgrade pip && \
    pip install uv

# Tạo môi trường ảo
RUN python -m venv /app/.venv
# Đặt PATH để sử dụng python và pip từ môi trường ảo
ENV PATH="/app/.venv/bin:$PATH"

# Copy file cấu hình và cài đặt dependencies vào môi trường ảo
COPY pyproject.toml .
RUN uv pip install -e .

# Cài đặt ngrok
RUN wget -q https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz && \
    tar xvzf ngrok-v3-stable-linux-amd64.tgz -C /usr/local/bin && \
    rm ngrok-v3-stable-linux-amd64.tgz

# Copy toàn bộ ứng dụng (trừ những file trong .dockerignore)
COPY . .

# Copy file .env vào container
COPY .env .

# Expose cổng cho máy chủ
EXPOSE 8080

# Tạo script khởi động
RUN echo '#!/bin/bash\n\
\n\
if [ -n "$NGROK_AUTHTOKEN" ]; then\n\
  echo "Cấu hình ngrok với authtoken..."\n\
  ngrok config add-authtoken $NGROK_AUTHTOKEN\n\
  \n\
  echo "Khởi động ngrok tunnel..."\n\
  nohup ngrok http 8080 --log=stdout > /app/ngrok.log 2>&1 &\n\
  \n\
  sleep 5\n\
  \n\
  NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | grep -o "https://[^\"]*")\n\
  if [ -n "$NGROK_URL" ]; then\n\
    echo "================================================================="\n\
    echo "🎉 NGROK TUNNEL CREATED SUCCESSFULLY!"\n\
    echo "================================================================="\n\
    echo "URL ngrok: $NGROK_URL"\n\
    echo "Sử dụng URL này để kết nối từ n8n.vbi-server.com"\n\
    echo "- SSE Endpoint: ${NGROK_URL}/sse"\n\
    echo "- Messages Endpoint: ${NGROK_URL}/messages/"\n\
    echo "================================================================="\n\
  else\n\
    echo "❌ Không thể lấy URL ngrok. Kiểm tra /app/ngrok.log để biết thêm chi tiết."\n\
  fi\n\
else\n\
  echo "⚠️ NGROK_AUTHTOKEN không được cấu hình. Ngrok tunnel sẽ không được tạo."\n\
  echo "Chỉ có thể truy cập máy chủ từ mạng nội bộ qua Docker IP."\n\
fi\n\
\n\
echo "Khởi động máy chủ mem0-mcp..."\n\
# Python bây giờ sẽ tự động được gọi từ môi trường ảo do ENV PATH\n\
exec python main_with_cors.py\n\
' > /app/start.sh && chmod +x /app/start.sh

# Lệnh mặc định khi container chạy
CMD ["/app/start.sh"]
