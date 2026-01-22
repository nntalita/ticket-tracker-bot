from ticket_bot.parser_old import parser

result = parser.check_route("Москва-Сочи")
print("Цена:", result['price'])