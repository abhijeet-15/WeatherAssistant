from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
import logging

logger = logging.getLogger(__name__)

class PromptManager:
    def __init__(self):
        base_dir = Path(__file__).parent.parent
        self.template_dir = base_dir / "templates"
        
        if not self.template_dir.exists():
            raise FileNotFoundError(f"Template directory not found at {self.template_dir}")

        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=select_autoescape(),
            trim_blocks=True,
            lstrip_blocks=True
        )

    def build_system_prompt(self, tools_list: list, extra_guidance: str = None) -> str:
        try:
            template = self.env.get_template("system.jinja")
            return template.render(
                tools=tools_list,
                extra_guidance=extra_guidance
            )
        except Exception as e:
            logger.error(f"failed to render the system prompt: {e}")
            raise

    
    def build_greeting(self, **kwargs) -> str:
        try:
            template = self.env.get_template("greeting.jinja")
            return template.render(**kwargs)
        except Exception as e:
            logger.error(f"failed to render the system prompt: {e}")
            raise



prompt_manager =  PromptManager()