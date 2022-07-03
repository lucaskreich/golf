
import requests
from lxml import html


# def get_index_2(player_id):
#     headers = {
#         "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36"}
#     url = f"https://cbg.bluegolf.com/bluegolf/cbg/handicap/{player_id}/index.htm"
#     webpage = requests.get(url, headers=headers)
#     index_web_page = webpage.text
#     print(index_web_page)
#     soup = BeautifulSoup(index_web_page, "html.parser")

#     hcp = soup.find(name="div", class_="h4")
#     print(hcp)

# Não é hcp_id, é perfil do jogador no bluegolf // Alterar futuramente
def get_index(player_id):

    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36"}
    url = f"https://cbg.bluegolf.com/bluegolf/cbg/handicap/{player_id}/index.htm"
    webpage = requests.get(url, headers=headers)
    tree = html.fromstring(webpage.content)
    a = tree.xpath(
        '/html/body/div[3]/div[2]/div[2]/div/div/div[1]/div/div/div/div[2]/div[2]/div[1]/strong')
    if a == []:

        return 0
    hcp_index = a[0].text

    if hcp_index[-1] == "M":
        hcp_index = hcp_index[:-1]

    return hcp_index


def calc_hcp_qn(index):
    if index == None:
        return 0
    ch = int(round(index * (135/113) + (69.2-72), 0))
    return ch

# A premiação obedecerá ao resultado net de cada jogador na tabela de classificação:
# Até 4 jogadores – 100% do prêmio ao primeiro colocado;
# De 05 a 10 jogadores – 70% do prêmio ao primeiro colocado e 30% para o segundo colocado;
# 11 jogadores ou mais – 60% ao primeiro, 30% ao segundo e 10% ao terceiro colocado.
