import discord
from hcskr import QuickTestResult, asyncSelfCheck, asyncUserLogin
import os
from dotenv import load_dotenv
import aiohttp
import json

bot = discord.Bot(intents = discord.Intents.all())

@bot.event
async def on_ready():
    print("I'm on ready! ✔️")

@bot.slash_command(description="HCS-BOT에 정보를 등록합니다.")
async def 등록(ctx, 이름: discord.Option(str, "이름 입력하기"), 
                    생년월일: discord.Option(str, "생일 입력하기"),
                    지역: discord.Option(str, "지역 입력하기"),
                    학교이름: discord.Option(str, "학교이름 입력하기"),
                    학교종류: discord.Option(str, "학교종류 고르기", choices=["초등학교", "중학교", "고등학교"]),
                    비밀번호: discord.Option(str, "비밀번호 입력하기")):

    original_message = await ctx.respond("잠시만 기다려주세요...", ephemeral=True)

    json_object = {
        "name": f"{이름}",
        "birth": f"{생년월일}",
        "area": f"{지역}",
        "schoolname": f"{학교이름}",
        "level": f"{학교종류}",
        "password": f"{비밀번호}"
    }

    login = await asyncUserLogin(이름, 생년월일, 지역, 학교이름, 학교종류, 비밀번호, session=aiohttp.ClientSession())

    if str(login.get('error')) == "True":
        return await original_message.edit_original_message(content=login.get('message'))
    
    with open(f"{ctx.user.id}.json", "w", encoding="UTF-8") as f:
        json.dump(json_object, f, ensure_ascii=False, indent=2)

    role = discord.utils.get(ctx.guild.roles, name="> Verified ✔️")

    await ctx.author.add_roles(role)

    await original_message.edit_original_message(content="가입 완료!")

@bot.slash_command(description="HCS-BOT를 통해 자가진단을 실행합니다.")
async def 자가진단(ctx, 신속항원검사: discord.Option(str, "검사키트 검사결과를 선택합니다.", choices=["음성 (Negative)", "양성 (Positive)"])):
    original_message = await ctx.respond("잠시만 기다려주세요...")

    if 신속항원검사 == "음성 (Negative)":

        with open(f"{ctx.user.id}.json", "r", encoding="UTF-8") as f:
            json_object = json.load(f)

            await asyncSelfCheck(name=json_object.get('name'),
                                birth=json_object.get('birth'),
                                area=json_object.get('area'),
                                schoolname=json_object.get('schoolname'),
                                level=json_object.get('level'),
                                password=json_object.get('password'),
                                quicktestresult=QuickTestResult.negative)

        return await original_message.edit_original_message(content="자가진단 완료! (음성, Negative)")
    
    elif 신속항원검사 == "양성 (Positive)":
        with open(f"{ctx.user.id}.json", "r", encoding="UTF-8") as f:
            json_object = json.load(f)

            await asyncSelfCheck(name=json_object.get('name'),
                                birth=json_object.get('birth'),
                                area=json_object.get('area'),
                                schoolname=json_object.get('schoolname'),
                                level=json_object.get('level'),
                                password=json_object.get('password'),
                                quicktestresult=QuickTestResult.positive)

load_dotenv()
bot.run(os.getenv('TOKEN'))
