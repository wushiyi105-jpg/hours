# 更新记录

## Unreleased

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
