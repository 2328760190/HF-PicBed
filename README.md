# HF-PicBed 🖼️

[![Hugging Face Space](https://img.shields.io/badge/🤗-HuggingFace%20Space-blue.svg)](https://huggingface.co/spaces/2328760190/HF-PicBed)
[![Demo](https://img.shields.io/badge/Demo-Live%20Preview-green.svg)](https://chb2026-image.hf.space)

基于Hugging Face Space打造的图床服务，兼容PicGo API v1.1规范，支持多种文件上传方式，自动将文件存储在Hugging Face Dataset并提供直链访问。

## 🌟 功能特性
- ✅ 完全兼容PicGo API v1.1规范
- 🚀 支持三种文件上传方式：
  - 二进制文件上传
  - Base64编码数据传输
  - 图片URL直传
- 🔒 可选API密钥鉴权
- 📦 自动存储到Hugging Face Dataset
- 🌐 生成可直接访问的图片URL
- ⚖️ 支持文件大小限制（默认10MB）

## 🚀 快速开始

### 基础请求
```bash
# 无鉴权上传
curl -X POST -F "source=@image.jpg" https://chb2026-image.hf.space/upload

# Base64上传示例
curl -X POST -d "source_b64=data:image/png;base64,iVBOR..." https://chb2026-image.hf.space/upload
```

### 带鉴权请求
```bash
# Header鉴权方式
curl -X POST \
  -H "X-API-Key: YOUR_KEY" \
  -F "source=@image.png" \
  https://your-space.hf.space/upload

# 参数鉴权方式
curl -X POST \
  -d "key=YOUR_KEY" \
  -F "source=@image.jpg" \
  https://your-space.hf.space/upload
```

## 📚 API文档

### 请求端点
```
POST /upload
```

### 请求参数
| 参数名 | 必填 | 描述 |
|--------|------|-----|
| source | 是 | 文件上传字段/BASE64字符串/图片URL |
| key    | 否 | API密钥（当使用参数鉴权时） |
| format | 否 | 响应格式（json/txt/redirect） |

### 响应格式
#### JSON响应（默认）
```json
{
  "status_code": 200,
  "status_txt": "OK",
  "image": {
    "url": "https://.../image.jpg",
    "filename": "20240520_123456_abc123.jpg",
    "size": 12345
  }
}
```

#### 纯文本响应
```
https://huggingface.co/datasets/.../image.jpg
```

#### 重定向响应
HTTP 302 跳转到图片直链

## 🛠 部署指南

### 准备工作
1. 创建Hugging Face账号
2. 新建Dataset(必须为公开)仓库（e.g. `username/images`）
3. 生成Hugging Face访问令牌（[设置页面](https://huggingface.co/settings/tokens)）

### Space部署步骤
1. 访问[创建新Space](https://huggingface.co/new-space)
2. 填写空间信息：
   - **SDK**：选择Docker
   - **仓库名**：自定义（如HF-PicBed）
   - **仓库类型**：Public(必须)
3. 上传项目文件
4. 设置环境变量：
   | 变量名 | 必填 | 示例值 |
   |--------|------|--------|
   | DATASET_ID | ✔️ | yourname/images |
   | HF_TOKEN | ✔️ | hf_xxxxxxxx |
   | MAX_SIZE | ❌ | 5（单位MB） |
   | API_KEY | ❌ | your_secret_key |
5. 部署完成后访问空间域名即可使用

## 🔧 环境配置
```python
# .env 示例(可在huggingface的space中的设置中添加，或创建.env文件)
DATASET_ID = "your_username/your_dataset"
HF_TOKEN = "hf_xxxxxxxxxxxxxxxx"
API_KEY = "your_optional_password"  # 非必填
MAX_SIZE = 10  # MB
```

## 🤝 贡献指南
欢迎提交Issue和PR！遇到问题请提供：
1. 复现步骤
2. 请求/响应详情
3. 环境信息

## 许可证
[MIT License](LICENSE)
