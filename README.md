# kar-sim-arena / arcade

一次性仿真产品仓。它是 KAR Squad 评估的「舞台」：一个刻意做小的真实产品（贪吃蛇 + 分数持久化），让三条工作道有真实可交付的东西。

**这不是生产项目。** 分支、tag、部署脚本都只服务评估；禁止真实用户数据与真实密钥。

## 运行

```bash
python3 -m arcade.server --port 8000   # http://127.0.0.1:8000
python3 -m unittest discover -s tests -t . -v
```

## 现状（起始基线）

- 游戏核心与静态页面可用，分数通过 `POST /api/score` 持久化到 JSON 文件。
- **还没有**排行榜页面、分页、登录、暗色模式完善。
- `deploy.py` 与 `docs/DEPLOY.md` 不一致：文档承诺 `--dry-run`，脚本尚未实现（Q-01 的种子缺陷）。

这些「缺口」是评估用例的起点，不是 bug 清单；每个用例都从固定 commit 起步，跑完分支即弃。

## 评估约定

- 隐藏验收测试**不在本仓**，由评估仓注入。
- CI 必须真实通过；不允许删除/跳过测试来变绿。
- 合并目标为 `develop`；`main` 只由人类发布。
