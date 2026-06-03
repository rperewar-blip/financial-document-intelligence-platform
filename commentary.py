import anthropic
import os
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(
    api_key=os.getenv('ANTHROPIC_API_KEY')
)

def generate_comparison_commentary(companies_data: list) -> str:
    data_str = ''

    for c in companies_data:
        data_str += f"\n{c['company']}: "
        data_str += f"Revenue ${c.get('revenue', 'N/A')}M, "
        data_str += f"Net Income ${c.get('net_income', 'N/A')}M, "
        data_str += f"EBITDA ${c.get('ebitda', 'N/A')}M\n"

    prompt = f'''
You are a senior equity research analyst writing a comparable company memo.

Based on the following extracted financial data, write a 3-4 paragraph professional analyst commentary.

Cover:
- relative revenue scale
- profitability differences
- balance sheet observations
- 2-3 specific insights a CFO or investor would care about

Use professional financial language.

Data:
{data_str}

Commentary:
'''

    msg = client.messages.create(
        model='claude-haiku-4-5-20251001',
        max_tokens=800,
        messages=[
            {
                'role': 'user',
                'content': prompt
            }
        ]
    )

    return msg.content[0].text
