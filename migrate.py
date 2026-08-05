#!/usr/bin/env python3
"""Hindsight 记忆迁移 v2：Cloud → 自建实例
端点（已验证 2026-08-05）：
  GET  /v1/default/banks/{bank}/memories/list?limit&offset  分页拉记忆
  POST /v1/default/banks/{bank}/memories                    RetainMemory batch
用法：
  export HINDSIGHT_CLOUD_KEY=<Cloud key>
  export HINDSIGHT_NEW_URL=https://<space>.hf.space
  export HINDSIGHT_NEW_KEY=<自建 key，可不设则复用 cloud>
  python3 migrate.py export    # 分页导出全部记忆 → hindsight_export.json
  python3 migrate.py import    # 分批导入新实例
说明：MVP 迁移记忆文本（content/context/timestamp），不迁移 documents/entities 全集。
"""
import json
import os
import sys
import urllib.request

CLOUD_URL = "https://api.hindsight.vectorize.io"
BANK = "hermes"
EXPORT_FILE = "hindsight_export.json"
PAGE = 100


def _req(url, key, method="GET", body=None):
    headers = {"Authorization": f"Bearer {key}"}
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"
    r = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(r, timeout=120) as resp:
        return json.loads(resp.read())


def export_bank():
    key = os.environ.get("HINDSIGHT_CLOUD_KEY")
    if not key:
        sys.exit("缺 HINDSIGHT_CLOUD_KEY")
    base = f"{CLOUD_URL}/v1/default/banks/{BANK}/memories/list"
    mems, total, offset = [], None, 0
    while True:
        page = _req(f"{base}?limit={PAGE}&offset={offset}", key)
        items = page.get("items", [])
        if total is None:
            total = page.get("total", 0)
        mems.extend(items)
        offset += len(items)
        print(f"  翻页 offset={offset} / total={total}", flush=True)
        if not items or (total and offset >= total):
            break
    with open(EXPORT_FILE, "w", encoding="utf-8") as f:
        json.dump({"total": len(mems), "memories": mems}, f, ensure_ascii=False, indent=2)
    print(f"✅ 导出 {len(mems)} 条 → {EXPORT_FILE}")


def import_bank():
    new_url = os.environ.get("HINDSIGHT_NEW_URL")
    key = os.environ.get("HINDSIGHT_NEW_KEY") or os.environ.get("HINDSIGHT_CLOUD_KEY")
    if not new_url or not key:
        sys.exit("缺 HINDSIGHT_NEW_URL / HINDSIGHT_NEW_KEY")
    data = json.load(open(EXPORT_FILE, encoding="utf-8"))
    mems = data["memories"]
    items = []
    for m in mems:
        ts = m.get("occurred_start") or m.get("date")
        items.append({
            "content": m.get("text", ""),
            "context": m.get("context"),
            "timestamp": ts,
            "metadata": {"fact_type": m.get("fact_type"), "proof_count": str(m.get("proof_count", ""))},
        })
    items = [it for it in items if it["content"].strip()]
    url = f"{new_url}/v1/default/banks/{BANK}/memories"
    for i in range(0, len(items), 100):
        _req(url, key, method="POST", body={"items": items[i:i + 100]})
        print(f"  已导入 {min(i + 100, len(items))}/{len(items)}", flush=True)
    print("✅ 导入完成")


if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "export"
    {"export": export_bank, "import": import_bank}[action]()