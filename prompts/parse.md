把一句口语拆成一条工时记录，输出 JSON：
{"project": "项目名", "minutes": 整数, "note": "做了什么", "confidence": 0-1}

- project 必须来自给定清单，拿不准就留空；
- minutes 必须在 1-1440，半天记 240；
- 不要编造项目或时长。