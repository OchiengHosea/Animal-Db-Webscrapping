BASE_URL = 'https://animals.fandom.com'
CLASSES = {'vertebrates':{
    'Birds':'Aves',
    'Mammals':'Mammalia',
    'Reptiles':'Reptilia',
    'Amphibians':'Amphibia',
    'Ray-finned Fisches':'Actinopterygii',
    'Cartillaginoues Fishes': 'Chondrichthyes'
}, 'invertebrates':'INVERTEBRATES'}

PATHS = {
    'total_number_in_category_xpath':'/html/body/div[4]/div[3]/div[5]/main/div[3]/div/p',
    'cat_page_mbrs_xpath':'/html/body/div[4]/div[3]/div[5]/main/div[3]/div/div[3]',
    'pagination_xpath':'/html/body/div[4]/div[3]/div[5]/main/div[3]/div/div[4]/a[1]' 
}