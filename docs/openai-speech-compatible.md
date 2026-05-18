# VoxCPM OpenAI Speech Compatible API

VoxCPM Server 提供兼容 OpenAI Audio Speech API 的 HTTP 接口，可通过 Docker 一键部署。

- 基础路径：`http://<host>:8000`
- 协议：REST JSON
- 编码：UTF-8

## 接口总览

| 方法   | 路径                 | 说明             |
| ------ | -------------------- | ---------------- |
| POST   | `/v1/audio/speech`   | 语音合成（核心） |
| GET    | `/v1/audio/voices`   | 可用音色列表     |
| GET    | `/v1/models`         | 可用模型列表     |
| GET    | `/health`            | 健康检查         |

---

## POST /v1/audio/speech

根据文本生成语音，支持流式和非流式两种模式。

### 请求参数

| 参数            | 类型     | 必填 | 默认值     | 说明                                                   |
| --------------- | -------- | ---- | ---------- | ------------------------------------------------------ |
| `model`         | string   | 否   | `"voxcpm2"`| 模型标识，固定为 `voxcpm2`                             |
| `input`         | string   | 是   | -          | 待合成文本                                             |
| `voice`         | string   | 否   | `"default"`| 音色名称，见下方音色列表                               |
| `response_format`| string  | 否   | `"mp3"`    | 非流式输出格式：`mp3` `wav` `flac` `pcm`               |
| `speed`         | float    | 否   | `1.0`      | 语速倍率，范围 `0.25 ~ 4.0`                            |
| `stream`        | bool     | 否   | `false`    | `true` 启用流式，`false` 非流式                        |
| `language`      | string   | 否   | `"Auto"`   | 语言，`"Auto"` 自动检测，或指定语言名                   |
| `instructions`  | string   | 否   | `null`     | 语音风格指令，与 voice 描述叠加                         |
| `instruct`      | string   | 否   | `null`     | `instructions` 的别名，二者取其一即可                   |
| `seed`          | int      | 否   | 配置文件值  | 随机种子，`-1` 不固定随机性，`>=0` 固定种子可复现       |

#### voice 与 instructions 的关系

`voice` 映射到一段预设的英文风格描述，`instructions` 会追加在预设描述之后。
最终控制指令格式为 `({voice_description}, {instructions}){input}`。
若 `voice=default` 且未提供 `instructions`，则不加任何前缀。

#### speed 与 CFG 的映射

`speed` 参数通过线性映射转换为模型内部 CFG (Classifier-Free Guidance) 值：

| speed | CFG  |
| ----- | ---- |
| 0.25  | 1.0  |
| 1.0   | 2.0  |
| 4.0   | 4.0  |

映射公式：当 `speed` 在 `(0.25, 4.0)` 区间时，`cfg = 1.0 + (speed - 0.25) * (3.0 / 3.75)`。

#### seed 与可复现生成

`seed` 参数控制音频生成的随机性，用于实现可复现的音色输出：

| seed 值 | 行为                               |
| ------- | ---------------------------------- |
| `-1`    | 不固定随机种子，每次生成结果不同   |
| `>= 0`  | 固定随机种子，相同输入可复现音色   |

- 请求未指定 `seed` 时，使用服务配置文件 `audio.seed` 的值（默认 `-1`）。
- 相同 `seed` + 相同输入文本 + 相同参考音频 = 可复现的音色输出。

### 非流式响应 (`stream: false`)

返回完整的音频文件。

**响应头：**

| Header               | 值                            |
| -------------------- | ----------------------------- |
| `Content-Type`       | `audio/mpeg` (mp3) 或 `audio/{format}` |
| `Content-Disposition`| `attachment; filename=speech.{format}` |

**支持的输出格式：**

| 格式    | response_format | Content-Type    |
| ------- | --------------- | --------------- |
| MP3     | `mp3`           | `audio/mpeg`    |
| WAV     | `wav`           | `audio/wav`     |
| FLAC    | `flac`          | `audio/flac`    |
| PCM     | `pcm`           | `audio/pcm`     |

音频参数：采样率 48000 Hz，单声道（mono）。

### 流式响应 (`stream: true`)

以分块方式持续返回 PCM 音频数据，适合低延迟播放场景。

**响应头：**

| Header                | 值              | 说明                   |
| --------------------- | --------------- | ---------------------- |
| `Content-Type`        | `audio/pcm`     | 裸 PCM 数据            |
| `X-Sample-Rate`       | `48000`         | 采样率 (Hz)            |
| `X-Bits-Per-Sample`   | `16`            | 每采样位深 (bit)       |
| `X-Channels`          | `1`             | 声道数                 |
| `X-Audio-Format`      | `pcm_s16le`     | PCM 子格式标识         |
| `X-Content-Type-Options` | `nosniff`   | MIME 嗅探防护          |

**PCM 数据格式：**

- 编码：16-bit signed little-endian (int16 LE)
- 采样率：48000 Hz
- 声道：1 (mono)
- 字节序：little-endian

**客户端消费建议：**

客户端应在开始播放前从响应头读取 `X-Sample-Rate`、`X-Bits-Per-Sample`、`X-Channels` 来正确配置播放器，而非硬编码采样率。

```python
import requests

resp = requests.post("http://localhost:8000/v1/audio/speech", json={
    "input": "你好世界",
    "stream": True,
}, stream=True)

sample_rate = int(resp.headers["X-Sample-Rate"])      # 48000
bits = int(resp.headers["X-Bits-Per-Sample"])          # 16
channels = int(resp.headers["X-Channels"])             # 1

for chunk in resp.iter_content(chunk_size=4096):
    play_pcm_chunk(chunk, sample_rate, bits, channels)
```

```go
resp, _ := http.Post(url, "application/json", body)
sampleRate := resp.Header.Get("X-Sample-Rate") // "48000"
bits := resp.Header.Get("X-Bits-Per-Sample")   // "16"
channels := resp.Header.Get("X-Channels")       // "1"
```

### 请求示例

**非流式（cURL）：**

```bash
curl -X POST http://localhost:8000/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{
    "model": "voxcpm2",
    "input": "Hello, this is a test.",
    "voice": "alloy",
    "response_format": "mp3",
    "speed": 1.0,
    "seed": 42
  }' \
  --output speech.mp3
```

**流式（Python）：**

```python
import requests

resp = requests.post("http://localhost:8000/v1/audio/speech", json={
    "model": "voxcpm2",
    "input": "这是一段流式语音合成测试。",
    "voice": "nova",
    "stream": True,
}, stream=True)

with open("output.pcm", "wb") as f:
    for chunk in resp.iter_content(chunk_size=4096):
        f.write(chunk)

# 转换为 WAV 播放：ffmpeg -f s16le -ar 48000 -ac 1 -i output.pcm output.wav
```

### 错误响应

| HTTP 状态码 | 含义                       |
| ----------- | -------------------------- |
| 200         | 成功                       |
| 422         | 请求参数校验失败           |
| 500         | 服务端内部错误（合成失败） |
| 503         | 模型尚未加载完成           |

---

## GET /v1/audio/voices

返回可用音色和语言列表。

**响应示例：**

```json
{
  "voices": [
    { "name": "default", "id": "default", "language": "auto" },
    { "name": "alloy",   "id": "alloy",   "language": "auto" },
    { "name": "echo",    "id": "echo",    "language": "auto" },
    { "name": "fable",   "id": "fable",   "language": "auto" },
    { "name": "onyx",    "id": "onyx",    "language": "auto" },
    { "name": "nova",    "id": "nova",    "language": "auto" },
    { "name": "shimmer", "id": "shimmer", "language": "auto" }
  ],
  "languages": [
    "Auto", "Arabic", "Burmese", "Chinese", "Danish", "Dutch",
    "English", "Finnish", "French", "German", "Greek", "Hebrew",
    "Hindi", "Indonesian", "Italian", "Japanese", "Khmer", "Korean",
    "Lao", "Malay", "Norwegian", "Polish", "Portuguese", "Russian",
    "Spanish", "Swahili", "Swedish", "Tagalog", "Thai", "Turkish",
    "Vietnamese"
  ]
}
```

### 预设音色

| 音色      | 风格描述                                   |
| --------- | ------------------------------------------ |
| `default` | 默认音色，无额外风格控制                   |
| `alloy`   | 中性音色，均衡清晰                         |
| `echo`    | 温暖男声，亲切对话感                       |
| `fable`   | 英式口音，富有表现力，适合叙事             |
| `onyx`    | 低沉男声，沉稳自信                         |
| `nova`    | 女声，友好活泼                             |
| `shimmer` | 柔和女声，温柔平静                         |

---

## GET /v1/models

返回可用模型列表（兼容 OpenAI /v1/models 格式）。

**响应示例：**

```json
{
  "object": "list",
  "data": [
    {
      "id": "voxcpm2",
      "object": "model",
      "created": 1716000000,
      "owned_by": "openbmb"
    }
  ]
}
```

---

## GET /health

服务健康检查。

**响应示例：**

```json
{
  "status": "healthy",
  "model_loaded": true,
  "gpu_available": true,
  "gpu_count": 1
}
```

**status 字段含义：**

| 值               | 含义                       |
| ---------------- | -------------------------- |
| `healthy`        | 模型已加载，GPU 可用       |
| `healthy_no_gpu` | 模型已加载，无 GPU (CPU)   |
| `loading`        | 模型正在加载中             |

---

## 部署

通过 Docker Compose 一键部署：

```bash
cd docker
cp .env.example .env
docker compose up -d
```

默认监听端口 `8000`，可通过 `.env` 文件或 `docker-compose.yml` 修改。

详见 [docker/README.md](../docker/README.md)。

---

## 与 OpenAI API 的差异

| 特性              | OpenAI                         | VoxCPM                        |
| ----------------- | ------------------------------ | ----------------------------- |
| 模型标识          | `tts-1`, `tts-1-hd`           | `voxcpm2`                     |
| 流式输出格式      | 优先 Opus                      | PCM (int16 LE, 48kHz, mono)   |
| 流式元信息        | 无                             | `X-Sample-Rate` 等响应头      |
| 语速控制          | 直接 speed 倍率                | speed 线性映射为 CFG 值       |
| voice 参数        | 内置音色                       | 内置音色 + instructions 叠加  |
| 语言选择          | 无                             | 支持 30 种语言自动/手动切换   |
| 声音克隆          | 不支持                         | 通过 `instructions` 或参考音频支持 |
| 可复现生成        | 不支持                         | 通过 `seed` 参数支持可复现音色     |
