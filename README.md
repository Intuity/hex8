[![Hex8 CI](https://github.com/Intuity/hex8/actions/workflows/ci.yaml/badge.svg)](https://github.com/Intuity/hex8/actions/workflows/ci.yaml)

# hex8
Building a simple CPU in a robust way

## Creating Archives for All Tools

```bash
for x in $(ls -d ./*/*/); do
    y=${x:2};
    z=$(echo ${y:0:$((${#y}-1))} | tr '/.' '__');
    echo "# Creating ${z}.zip";
    zip -r ${z}.zip $x;
done
```

## Uploading to Cloudflare R2

```bash
aws s3api put-object \
          --endpoint-url https://<account>.r2.cloudflarestorage.com \
          --bucket <bucket> \
          --key <TARGET> \
          --body <LOCAL>
```
