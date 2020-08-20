# Get all of the mentioned education details
def get_education(item):
  institute = item.find("h3", class_ = 'pv-entity__school-name t-16 t-black t-bold').text

  try:
    degree_date = item.find("p", class_ = 'pv-entity__dates t-14 t-black--light t-normal').find_all("span")[1].text.strip()
  except:
    degree_date = ''

  try:
    degree = ' \u2022 ' + item.find("p", class_ = 'pv-entity__secondary-title pv-entity__degree-name t-14 t-black t-normal').find_all("span")[1].text
  except:
    degree = ''

  try:
    field = ', ' + item.find("p", class_ = 'pv-entity__secondary-title pv-entity__fos t-14 t-black t-normal').find_all("span")[1].text
  except:
    field = ''

  try:
    desc = item.find("p", class_ = 'pv-entity__description t-14 t-normal mt4')
    for tag in desc.select('span'):
      tag.extract()
    desc = '\n' + ' \u2022 ' + desc.text.replace('\n', '').strip()
  except:
    desc = ''

  try:
    extra = ' \u2022 ' + item.find("p", class_ = 'pv-entity__secondary-title t-14 t-black--light t-normal').text
  except:
    extra = ''

  data = institute + degree + field + ' \u2022 ' + degree_date + extra + desc
  return data
