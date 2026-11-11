# Deploying arcade

```bash
python3 deploy.py --dry-run   # print the planned steps, change nothing
python3 deploy.py --apply     # copy static assets and restart the service
```

`--dry-run` and `--apply` are mutually exclusive; pass exactly one.
