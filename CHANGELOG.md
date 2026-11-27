# 更新记录

## Unreleased

- 新增 `statement --month`：一次输出月度结算 CSV + 同名邮件正文，按项目汇总工时、税额、含税合计
- 新增 4 档费率与 4 种税率数据文件，账单与正文共用同一口径
- 种子扩为 3 个项目、31 条工时、6420 分钟；实测 107 小时、含税 31,842.40 元
- `0001_init` 改为显式 `op.create_table` / `op.create_index`，运行期走 `alembic upgrade`
- `app/` 只依赖 `ports`，新增内存假实现用例
- 开 ruff `E2`/`E3`；CI 增加 `docker build` 与 `/health` 探活

## 1.0.0

- 中文口语时长解析与项目校验
- 同日同项目重叠检测
- 工时 / 金额双预算
- 甲方账单 CSV（与周报同口径）
- 单日 16 小时上限
- 每周汇总任务（幂等键 `hours:{week}`）
