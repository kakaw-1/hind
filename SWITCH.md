# Hermes 端切换：Hindsight Cloud → 自建 HF Space

## 当前配置（/opt/data/hindsight/config.json）
```json
{
  "mode": "cloud",
  "apiKey": "hsk_70aabcb0ed9fc1d1a947a0837a94d463_a64ec9dcc8ffece9",
  "banks": { "hermes": { "bankId": "hermes", "budget": "mid", "enabled": true } }
}
```

## 切换后（diff 预览，待你确认后执行）
```diff
 {
-  "mode": "cloud",
+  "mode": "local_external",
   "apiKey": "hsk_70aabcb0ed9fc1d1a947a0837a94d463_a64ec9dcc8ffece9",
+  "apiUrl": "https://<your-space>.hf.space",
   "banks": { "hermes": { "bankId": "hermes", "budget": "mid", "enabled": true } }
 }
```
说明：
- `mode=local_external` + `apiUrl` 指向 HF Space（插件 schema 已支持，见 config_schema.py:28-33, 46-53）
- apiKey 保留原值或换成自建实例生成的 key（新实例未启用认证可暂时留空/原样）
- bank 结构不变（bankId=hermes 已在自建实例通过 import 迁移）

## 回滚预案（一键）
```bash
cp /opt/data/hindsight/config.json /opt/data/hindsight/config.json.bak-$(date +%s)
# 切回 Cloud：
cp /opt/data/hindsight/config.json.cloud-backup /opt/data/hindsight/config.json
# 或手工把 mode 改回 "cloud"、删掉 apiUrl 字段
```
切换后 memory provider 无需重启（hindsight 插件按记忆描述"可热生效"），如不生效执行
`hermes memory setup` 重新激活一次。

## 验证清单
1. `curl https://<space>.hf.space/health` → 200
2. 切换后手动发一条 `hindsight_retain` 测试 → 成功
3. 下一轮对话开头观察是否注入 recall 记忆（中文检索）
4. 跑 `python3 migrate.py import` 后，`recall` 一条旧记忆验证迁移完整性
