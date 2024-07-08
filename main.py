from fastapi import *
from fastapi.responses import *
from fastapi.middleware.cors import *
from function import *
from schema import *
from variable import *
from redis.commands.json.path import Path
import base64

app = FastAPI(
    title="sqlr.kr",
    summary="Made By Dev_Nergis(BACK), imnyang(BACK), ny64(FRONT)",
    description="sqlr.kr is a URL shortening service.",
    version="5.0.2")

# noinspection PyTypeChecker
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# noinspection DuplicatedCode
@app.post("/shorten", response_class=ORJSONResponse)
async def shorten_link(body: Link):
    key = await anext(generate_key())
    url_hash = base64.b85encode(body.url.encode())

    if body.password is None:
        hooks = {"url": url_hash.hex()}
    else:
        salt, password_hash = Security(body.password).hash_new_password()
        hooks = {"url": url_hash.hex(), "salt": salt.hex(), "password_hash": password_hash.hex()}

    db = redis.Redis(connection_pool=pool(KEY_DB))
    await db.json().set(key, Path.root_path(), hooks)
    await db.close()

    return {"short_link": f"{DOMAIN}/{key}"}


# noinspection DuplicatedCode
@app.post("/shorten_emoji", response_class=ORJSONResponse)
async def shorten_emoji_link(body: Link):
    key = await anext(generate_emoji_key())
    url_hash = base64.b85encode(body.url.encode())

    if body.password is None:
        hgQs = {"url": url_hash.hex()}
    else:
        salt, password_hash = Security(body.password).hash_new_password()
        hgQs = {"url": url_hash.hex(), "salt": salt.hex(), "password_hash": password_hash.hex()}

    db = redis.Redis(connection_pool=pool(EMOJI_DB))
    await db.json().set(key, Path.root_path(), hgQs)
    await db.close()

    return {"short_link": f"{DOMAIN}/{key}"}


# noinspection DuplicatedCode
@app.post("/tossDonate", response_class=ORJSONResponse)
async def shorten_donate(body: LinkDonate):
    if not body.url.startswith("https://toss.me"):
        return ORJSONResponse(content={"error": "이 기능은 무조건 'https://toss.me'로 시작해야해요."}, status_code=400)

    key = await anext(generate_key())
    url_hash = base64.b85encode(body.url.encode())
    hgQs = {"url": url_hash.hex()}

    db = redis.Redis(connection_pool=pool(DONATE_DB))
    await db.json().set(key, Path.root_path(), hgQs)
    await db.close()

    return {"short_link": f"{DOMAIN}/d/{key}"}


# noinspection DuplicatedCode
@app.post("/shorten_qr_code", response_class=FileResponse)
async def generate_qr_code(body: LinkQRCODE, file: Optional[bool] = None):
    key = await anext(generate_key())
    url_hash = base64.b85encode(body.data.encode())
    hgQs = {"url": url_hash.hex()}

    db = redis.Redis(connection_pool=pool(KEY_DB))
    await db.json().set(key, Path.root_path(), hgQs)
    await db.close()

    img = generate_qr_code_image(f"{DOMAIN}/{key}", body.version, body.error_correction, body.box_size, body.border,
                                 body.mask_pattern).read()

    if file:
        return Response(img)
    else:
        return HTMLResponse(content=f'<img src="data:image/png;base64,{base64.b64encode(img).decode()}" />')


# noinspection PyBroadException
@app.get("/{short_key}")
async def redirect_to_original(request: Request, short_key: str, password: Optional[str] = None):
    db_c = redis.Redis(connection_pool=pool(KEY_DB))
    db = await db_c.json().jsonget(short_key, Path.root_path())
    await db_c.close()

    if db is None:
        db_c = redis.Redis(connection_pool=pool(EMOJI_DB))
        db = await db_c.json().jsonget(short_key, Path.root_path())
        await db_c.close()

    try:
        url = bytes.fromhex(db["url"]).decode("utf-8")
        url = base64.b85decode(url).decode("utf-8")
    except:
        return HTTP_404(request)

    try:
        salt = bytes.fromhex(db["salt"])
        password_hash = bytes.fromhex(db["password_hash"])
    except:
        return RedirectResponse(url)

    if isinstance(password, str):
        if Security(str(password), salt, password_hash).is_correct_password():
            return RedirectResponse(url)
        else:
            return HTTP_401(request)
    else:
        return HTTP_401(request)


# noinspection PyBroadException
@app.get("/d/{short_key}")
async def redirect_to_original(request: Request, short_key: str):
    db_c = redis.Redis(connection_pool=pool(DONATE_DB))
    db = await db_c.json().jsonget(short_key, Path.root_path())
    await db_c.close()

    try:
        url = bytes.fromhex(db["url"]).decode("utf-8")
        url = base64.b85decode(url).decode("utf-8")
    except:
        return HTTP_404(request)

    return RedirectResponse(url)

# 코체 멍청이
