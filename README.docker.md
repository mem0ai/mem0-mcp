# mem0-mcp với Docker

Hướng dẫn này sẽ giúp bạn cài đặt và chạy mem0-mcp trong Docker, giúp kết nối từ n8n.vbi-server.com đến máy chủ mem0-mcp cục bộ.

## Yêu cầu cài đặt

-   Docker & Docker Compose
-   Tài khoản mem0 và API key
-   (Tùy chọn) Tài khoản ngrok và authtoken

## Thiết lập môi trường

1. Sao chép file `.env.example` thành `.env`:

```bash
cp .env.example .env
```

2. Chỉnh sửa file `.env` và điền thông tin:

```
# API key của mem0 (bắt buộc)
MEM0_API_KEY=your_mem0_api_key_here

# Auth token của ngrok (tùy chọn, nhưng cần thiết để tạo tunnel)
NGROK_AUTHTOKEN=your_ngrok_authtoken_here
```

## Chạy mem0-mcp với Docker

### Xây dựng và khởi động container

```bash
docker-compose up -d --build
```

Lệnh này sẽ:

-   Xây dựng image Docker cho mem0-mcp
-   Khởi động container trong chế độ nền (detached mode)

### Xem logs để lấy URL ngrok

```bash
docker-compose logs mem0-mcp
```

Nếu bạn đã cung cấp NGROK_AUTHTOKEN, bạn sẽ thấy URL ngrok trong logs:

```
=================================================================
🎉 NGROK TUNNEL CREATED SUCCESSFULLY!
=================================================================
URL ngrok: https://xxxx-xx-xx-xxx-xx.ngrok-free.app
Sử dụng URL này để kết nối từ n8n.vbi-server.com
- SSE Endpoint: https://xxxx-xx-xx-xxx-xx.ngrok-free.app/sse
- Messages Endpoint: https://xxxx-xx-xx-xxx-xx.ngrok-free.app/messages/
=================================================================
```

### Truy cập giao diện ngrok

Bạn có thể truy cập giao diện ngrok tại:

```
http://localhost:4040
```

## Kết nối từ n8n.vbi-server.com

Sau khi nhận được URL ngrok, bạn có thể sử dụng các endpoints sau để kết nối từ n8n:

-   **SSE Endpoint**: `https://xxxx-xx-xx-xxx-xx.ngrok-free.app/sse`
-   **Messages Endpoint**: `https://xxxx-xx-xx-xxx-xx.ngrok-free.app/messages/`

Tham khảo file `n8n_integration_guide.md` để biết thêm chi tiết về cách cấu hình n8n.

## Dừng và xóa container

```bash
# Dừng container
docker-compose stop

# Dừng và xóa container
docker-compose down

# Dừng, xóa container và xóa volumes
docker-compose down -v
```

## Các lệnh Docker hữu ích

```bash
# Xem logs realtime
docker-compose logs -f mem0-mcp

# Bật lại container đã dừng
docker-compose start

# Khởi động lại container
docker-compose restart mem0-mcp

# Truy cập shell trong container
docker-compose exec mem0-mcp bash
```

## Xử lý sự cố

### 1. Không thể kết nối với máy chủ

-   Kiểm tra logs container để xem máy chủ đã khởi động thành công chưa
-   Kiểm tra URL ngrok trong logs container
-   Đảm bảo cổng 8080 và 4040 không bị sử dụng bởi ứng dụng khác

### 2. Lỗi ngrok

-   Kiểm tra NGROK_AUTHTOKEN trong file .env
-   Xem logs ngrok tại /app/ngrok.log trong container:
    ```bash
    docker-compose exec mem0-mcp cat /app/ngrok.log
    ```

### 3. Lỗi mem0

-   Kiểm tra MEM0_API_KEY trong file .env
-   Xem logs của máy chủ mem0-mcp để tìm thông báo lỗi
