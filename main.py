import disnake
from disnake.ext import commands
from random import randint
import shelve

class Character:

    def __init__(self, name, strength, agility, stamina, intelligence, vigilance, perception):
        self.name = name
        self.strength = strength
        self.agility = agility
        self.stamina = stamina
        self.intelligence = intelligence
        self.vigilance = vigilance
        self.perception = perception


bot = commands.Bot(command_prefix=".", help_command=None, intents=disnake.Intents.all())

@bot.event
async def on_ready():
    print(f"Bot {bot.user} is ready to work.")


# dicetype - тип кубика, наприклад: d6, 2d12
# modifier - модифікатор який додається до результату кубика, не є обов'язковим
# visibility - впливає на подачу результату: 
# якщо дорівнює False, то виводить лише кінцевий результат, 
# якщо True, то виводить більш детальний результат.
@bot.slash_command()
async def roll(inter, dicetype: str, modifier=0, visibility: str="False"):
    # розділимо dicetype на два значення: кількість підкидань та тип кубика
    x = dicetype.split('d')
    if x[0] == '':
        numdice = 1
        dice = int(x[1])
    else:
        numdice = int(x[0])
        dice = int(x[1])
    rollResult = 0
    result = ""
    # перевіряє чи тип кубика більше 1
    if dice > 1:
        # робимо генерацію числа для кожного кидка
        for x in range(0, numdice):
            r = randint(1, dice)
            rollResult += r
        # перевіряє чи модифікатор дорівнює нулю
        # якщо так, то повертає результат без модифікатора
        # якщо ні, то повертає результат з модифікатором
        if modifier != 0:
            if int(modifier) > 0:
                if visibility == "True":
                    result += "Result: {}+{}={}".format(rollResult, modifier, (rollResult+int(modifier)))
                else:
                    result += "Result: {}".format(rollResult+int(modifier))
                await inter.send(str(result))
            else:
                if visibility == "True":
                    result += "Result: {}{}={}".format(rollResult, modifier, (rollResult+int(modifier)))
                else:
                    result += "Result: {}".format(rollResult+int(modifier))
                await inter.send(str(result))
        else:
            result += "Result: {}".format(rollResult)
            await inter.send(str(result))
    else:
        await inter.send("Dice type can't be lower than 1.")

@bot.slash_command()
async def croll(inter, dicetype: str, char_name: str, property: str, visibility: str="False"):
    # визначаємо кількість кидків та тип кубика
    x = dicetype.split('d')
    if x[0] == '':
        numdice = 1
        dice = int(x[1])
    else:
        numdice = int(x[0])
        dice = int(x[1])
    # використовуючи модуль shelve дістанемо дані для модифікатора,
    # основуючись на імені персонажа та зазначеній характеристиці,
    # які вже внесені в базу данних
    db = shelve.open('characters.txt')
    char = db[char_name]
    if property not in dir(char):
        await inter.send("Character {} has no property called {}.".format(char_name, property))
    else:
        modifier = getattr(db[char_name], property)
        rollResult = 0
        result = ""
        # повторюємо кроки ті ж, що і в команді roll
        if dice > 1:
            # робимо генерацію числа для кожного кидка
            for x in range(0, numdice):
                r = randint(1, dice)
                rollResult += r
            # перевіряє чи модифікатор дорівнює нулю
            # якщо так, то повертає результат без модифікатора
            # якщо ні, то повертає результат з модифікатором
            if modifier != 0:
                if int(modifier) > 0:
                    if visibility == "True":
                        result += "Result: {}+{}={}".format(rollResult, modifier, (rollResult+int(modifier)))
                    else:
                        result += "Result: {}".format(rollResult+int(modifier))
                    await inter.send(str(result))
                else:
                    if visibility == "True":
                        result += "Result: {}{}={}".format(rollResult, modifier, (rollResult+int(modifier)))
                    else:
                        result += "Result: {}".format(rollResult+int(modifier))
                    await inter.send(str(result))
            else:
                result += "Result: {}".format(rollResult)
                await inter.send(str(result))
        else:
            await inter.send("Dice type can't be lower than 1.")

# команда для створення персонажа у базі даних
@bot.slash_command()
async def create_char(inter, char_name, strength=0, agility=0, stamina=0, intelligence=0, vigilance=0, perception=0):
    db = shelve.open('characters.txt')
    if char_name in db:
        db.close()
        await inter.send("Character with name {} is already exsist.".format(char_name))
    else:
        db[f'{char_name}'] = Character(char_name, strength, agility, stamina, intelligence, vigilance, perception)
        db.close()
        await inter.send("Character {} was created. Stats: strength={}, agility={}, stamina={}, intelligence={}, vigilance={}, perception={}.".format(char_name, strength, agility, stamina, intelligence, vigilance, perception))

# команда для зміни однієї з характеристик персонажа або створення нової
@bot.slash_command()
@commands.has_permissions(administrator=True)
async def add_property(inter, char_name, property, new_value):
    db = shelve.open('characters.txt')
    if char_name not in db:
        db.close()
        await inter.send("There's no character with name {}.".format(char_name))
    elif property not in dir(db):
        char = db[char_name]
        setattr(char, property, new_value)
        db[char_name] = char
        db.close()
        await inter.send("For character {} was created a new property called {} with value {}.".format(char_name, property, new_value))
    else:
        char = db[char_name]
        setattr(char, property, new_value)
        db[char_name] = char
        db.close()
        await inter.send("For character {} value of {} was changed to {}.".format(char_name, property, new_value))

# команда для видалення одніїєї з характеристик персонажа
@bot.slash_command()
@commands.has_permissions(administrator=True)
async def delete_property(inter, char_name, property):
    db = shelve.open('characters.txt')
    char = db[char_name]
    if char_name not in db:
        db.close()
        await inter.send("There's no character with name {}.".format(char_name))
    elif property not in dir(char):
        db.close()
        await inter.send("Character {} has no property called {}.".format(char_name, property))
    else:
        delattr(char, property)
        db[char_name] = char
        db.close()
        await inter.send("For character {} property called {} was deleted.".format(char_name, property))

# команда для видалення персонажу з бази даних
@bot.slash_command()
@commands.has_permissions(administrator=True)
async def delete_char(inter, char_name):
    db = shelve.open('characters.txt')
    if char_name not in db:
        db.close()
        await inter.send("There's no character with name {}.".format(char_name))
    else:
        del db[char_name]
        db.close()
        await inter.send("Character {} was deleted from list.".format(char_name))
    

bot.run("TOKEN")