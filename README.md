# Hindsight HF Space 部署清单（Aiven 免费 PG + HF 老号 Docker）

## 第 1 步：Aiven 建 PostgreSQL（免费）
1. https://console.aiven.io 注册（无信用卡），选 Aiven for PostgreSQL
2. 区域选 **Frankfurt**（离 Clever Cloud 巴黎近）
3. 版本 **16**（≥14 即可），Plan 选 **Startup-1（免费）**，单节点
4. 建库后（dashboard → Connection info）拿 **URI 连接串**：`postgresql://user:pass@host:port/db`
5. IP allowlist：放行 Hindsight 所在地（HF/CC 出口 IP），或先设 `0.0.0.0/0`（+SSL）测试
6. 用 psql 或 Adminer 执行启用向量扩展：
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```
   （Hindsight 启动时会自动建表/迁移 schema）

## 第 2 步：HF 老号建 Docker Space
1. huggingface.co → 右上角 **New Space**
2. SDK 选 **Docker**，硬件 **CPU basic（免费）**，Private 或 Public 均可
3. 用 git 推送（或新建 Space 时填仓库）：
   - 把本目录 `Dockerfile` 作为 Space 仓库根目录的 `Dockerfile`
   - HF 会用 `FROM ghcr.io/vectorize-io/hindsight:latest` 构建
4. Settings → **Variables and secrets** 填下表全部环境变量
5. 等构建完成，Space 状态变 Running，得到公网地址 `<your-space>.hf.space`

## 第 3 步：环境变量（HF Space → Variables）

| 变量 | 值 | 说明 |
|---|---|---|
| `HINDSIGHT_API_DATABASE_URL` | Aiven URI | 外部数据库（数据不随 Space rebuild 丢） |
| `HINDSIGHT_API_LLM_PROVIDER` | `openai` | 用 OpenAI 兼容端点接 deepseek |
| `HINDSIGHT_API_LLM_BASE_URL` | `https://no.bibd.cc.cd/v1` | 你的代理端点 |
| `HINDSIGHT_API_LLM_API_KEY` | 你的 key | [REDACTED] |
| `HINDSIGHT_API_LLM_MODEL` | `deepseek-v4-flash` | 按你的具体模型名 |
| `HINDSIGHT_API_EMBEDDINGS_PROVIDER` | `local` | full 镜像内置本地模型 |
| `HINDSIGHT_API_EMBEDDINGS_LOCAL_MODEL` | `BAAI/bge-m3` | **多语言/中文**（替代默认英文 bge-small） |
| `HINDSIGHT_API_RERANKER_PROVIDER` | `local` | full 内置 MiniLM 重排 |
| `HINDSIGHT_API_WORKER_ID` | `hf-hindsight-01` | 固定，防重启任务卡死 |
| `HINDSIGHT_API_BANK_ID` | `hermes` | 与 Hermes 端一致 |

## 第 4 步：保活（你说由你来）
- 目标 1：HF Space（48h 不活跃睡眠，冷启动 2-5 分钟）
- 目标 2：Aiven 免费 PG（无活动自动关机）
- 建议：每 20-30 分钟打一次 `<space>.hf.space/health`（或任一 recall 接口），两者一起保活

## 第 5 步：Hermes 切换（我在确认后做，含回滚备份）
- 改 `config.json`：`mode=local_external` + `api_url=https://<space>.hf.space` + API key
- 切换前备份旧配置，可一键回滚

## 成本
Aiven 免费 + HF Space 免费 + deepseek key 复用 = **€0/月**