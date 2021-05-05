# Captcha API
![Open Source? Yes!](https://badgen.net/badge/Open%20Source%20%3F/Yes%21/blue?icon=github)

[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)

## Info
The API is live at [PythonAnywhere](https://pythonanywhere.com/) (specifically, https://ammarsysdev.pythonanywhere.com/). Tell us [here](https://github.com/Ammar-sys/captchaAPI/issues) if you run into issues, discord works as well. (ammar#1197)

## USAGE

### Wrappers

 - [JavaScript](https://www.npmjs.com/package/essentials-captcha)
 - [Repository & Creator](https://github.com/SpeckyYT/essentials-captcha#readme)

### Manual Usage

Simply make a HTTP get request to the API endpoint and treat it like a JSON.

```python
import requests

response = requests.get('https://ammarsysdev.pythonanywhere/api/img').json()

print(response["solution"], response["url"])
```

or, if you'd like a async request

```python
import aiohttp
import asyncio

async def main():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://ammarsysdev.pythonanywhere.com/api/img') as responseget:
            return await responseget.json()

loop = asyncio.get_event_loop()
response = loop.run_until_complete(main())
print(response["solution"], response["url"])
```

For more examples check out https://ammarsysdev.pythonanywhere.com/examples !
This version is a new, fast and completely rewritten API, originally by Vixen, which was discontinued.
