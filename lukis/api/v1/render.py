import base64
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from ...common import chrome_pool


render_router = APIRouter()

class ViewPort(BaseModel):
    width: int
    height: int
    is_mobile: bool


class ScreenshotOptions(BaseModel):
    type: Optional[str] = "jpeg"
    quality: int = 50
    full_page: bool = True


class RenderRequest(BaseModel):
    url: str
    screenshot: Optional[ScreenshotOptions] = None
    viewport: Optional[ViewPort] = None
    js_source: Optional[str] = None


class RenderReponse(BaseModel):
    screenshot: Optional[str] = None
    html: str


@render_router.post("", tags=["Render"], response_model=RenderReponse)
async def render(req: RenderRequest):
    async with chrome_pool.get_connection() as browser:
        page = await browser.newPage()
        if req.viewport is not None:
            await page.emulate(
                options={
                    "viewport": {
                        "width": req.viewport.width,
                        "height": req.viewport.height,
                        "isMobile": req.viewport.is_mobile
                    }
                }
            )
        await page.goto(req.url)
        if req.js_source:
            await page.evaluate(req.js_source)
        html = await page.content()
        image = None
        if req.screenshot is not None:
            image = await page.screenshot(
                options={
                    "type": req.screenshot.type,
                    "quality": req.screenshot.quality,
                    "fullPage": req.screenshot.full_page,
                }
            )

        await page.close()
        
        return RenderReponse(
            screenshot=base64.standard_b64encode(image) if image else None,
            html=html,
        )