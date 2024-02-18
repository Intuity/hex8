# hex8
Building a simple CPU in a robust way

## Creating Archives for All Tools

```bash```
for x in $(ls -d ./*/*/); do
    y=${x:2};
    z=$(echo ${y:0:$((${#y}-1))} | tr '/.' '__');
    echo "# Creating ${z}.zip";
    echo zip -r ${z}.zip $x;
done
```
