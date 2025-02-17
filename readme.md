# OpenAI grading fix

## Usage

```
response1 = ...
response2 = ...

ans1 = lowlevel_extract(response1)
ans1 = lowlevel_normalize(ans1)

ans2 = lowlevel_extract(response2)
ans2 = lowlevel_normalize(ans2)

print(is_quiv(ans1,ans2)))
```
