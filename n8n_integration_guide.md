# Hướng dẫn tích hợp n8n.vbi-server.com với mem0-mcp

## Tổng quan

Tài liệu này hướng dẫn cách kết nối n8n.vbi-server.com với máy chủ mem0-mcp cục bộ thông qua ngrok tunnel.

## Cài đặt và cấu hình

### 1. Cài đặt ngrok (đã hoàn thành)

```bash
brew install ngrok
```

### 2. Đăng ký và cấu hình ngrok

> **Quan trọng**: Ngrok yêu cầu tài khoản và xác thực trước khi sử dụng.

1. Đăng ký tài khoản tại: https://dashboard.ngrok.com/signup

2. Sau khi đăng ký, lấy authtoken từ: https://dashboard.ngrok.com/get-started/your-authtoken

3. Cấu hình ngrok với authtoken:

```bash
ngrok config add-authtoken YOUR_AUTH_TOKEN
```

Thay `YOUR_AUTH_TOKEN` bằng token bạn nhận được từ trang web ngrok.

### 3. Chạy máy chủ mem0-mcp với CORS (đã hoàn thành)

```bash
cd mem0-mcp
source .venv/bin/activate
python main_with_cors.py
```

### 4. Tạo tunnel ngrok đến máy chủ cục bộ

Mở terminal mới và chạy:

```bash
./mem0-mcp/start_ngrok.sh
```

Sau khi chạy, ngrok sẽ tạo một URL công khai, ví dụ:

```
Forwarding  https://xxxx-xx-xx-xxx-xx.ngrok-free.app -> http://localhost:8080
```

### 5. Cấu hình n8n để sử dụng URL ngrok

#### 5.1 Endpoints quan trọng

Với URL ngrok là `https://xxxx-xx-xx-xxx-xx.ngrok-free.app` (thay thế bằng URL thực tế của bạn):

-   **SSE Endpoint**: `https://xxxx-xx-xx-xxx-xx.ngrok-free.app/sse`
-   **Messages Endpoint**: `https://xxxx-xx-xx-xxx-xx.ngrok-free.app/messages/`

#### 5.2 Tools mem0-mcp có sẵn

Máy chủ mem0-mcp cung cấp 3 công cụ:

1. **add_coding_preference**: Lưu trữ mã và mẫu lập trình
2. **get_all_coding_preferences**: Lấy tất cả mã đã lưu
3. **search_coding_preferences**: Tìm kiếm các đoạn mã phù hợp

#### 5.3 Cấu hình HTTP Request trong n8n

Khi tạo một HTTP Request node trong n8n, sử dụng các mẫu sau:

**Kết nối SSE**:

-   URL: `https://xxxx-xx-xx-xxx-xx.ngrok-free.app/sse`
-   Method: `GET`
-   Headers:
    -   `Accept`: `text/event-stream`

**Gọi tool add_coding_preference**:

-   URL: `https://xxxx-xx-xx-xxx-xx.ngrok-free.app/messages/`
-   Method: `POST`
-   Body:

```json
{
    "type": "tool_call",
    "tool_call": {
        "id": "add_preference_call",
        "function": {
            "name": "add_coding_preference",
            "arguments": {
                "text": "// Mã JavaScript mẫu\nfunction calculateSum(a, b) {\n  return a + b;\n}"
            }
        }
    }
}
```

**Gọi tool search_coding_preferences**:

-   URL: `https://xxxx-xx-xx-xxx-xx.ngrok-free.app/messages/`
-   Method: `POST`
-   Body:

```json
{
    "type": "tool_call",
    "tool_call": {
        "id": "search_call",
        "function": {
            "name": "search_coding_preferences",
            "arguments": {
                "query": "function tính tổng"
            }
        }
    }
}
```

### 6. Lưu ý quan trọng

-   URL ngrok thay đổi mỗi khi khởi động lại (phiên bản miễn phí)
-   Đăng ký ngrok Pro để có URL tĩnh không thay đổi
-   Tunnel ngrok tự động đóng sau 2 giờ không hoạt động (phiên bản miễn phí)
-   Đảm bảo cập nhật URL trong cấu hình n8n mỗi khi URL ngrok thay đổi

## Troubleshooting

### Lỗi xác thực ngrok

Nếu bạn gặp lỗi:

```
ERROR: authentication failed: Usage of ngrok requires a verified account and authtoken.
```

Hãy đảm bảo bạn đã:

1. Đăng ký tài khoản tại https://dashboard.ngrok.com/signup
2. Lấy authtoken từ https://dashboard.ngrok.com/get-started/your-authtoken
3. Cấu hình ngrok với lệnh `ngrok config add-authtoken YOUR_AUTH_TOKEN`

### CORS errors

Nếu gặp lỗi CORS, hãy kiểm tra:

-   Máy chủ mem0-mcp đang chạy với file `main_with_cors.py`
-   Headers trong HTTP Request được thiết lập đúng

### Connection errors

Nếu không thể kết nối:

-   Kiểm tra tunnel ngrok vẫn hoạt động
-   Đảm bảo máy chủ mem0-mcp đang chạy
-   Kiểm tra URL ngrok được sử dụng chính xác trong cấu hình n8n
