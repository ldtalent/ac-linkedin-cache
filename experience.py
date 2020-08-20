# Gets detail of an experience
def get_detail(value):
  interval = value.find("h4", class_ = 'pv-entity__date-range t-14 t-black--light t-normal').find_all("span")[1].text
  duration = value.find("h4", class_ = 't-14 t-black--light t-normal').find_all("span")[1].text

  try:
    desc = value.find("p", class_ = 'pv-entity__description t-14 t-black t-normal inline-show-more-text inline-show-more-text--is-collapsed ember-view')
    for tag in desc.select('span'):
      tag.extract()
    desc = '\n' + ' \u2022 ' + desc.text.replace('\n', '').strip()
  except:
    desc = ''
  
  try:
    location = ' \u2022 ' + value.find("h4", class_ = 'pv-entity__location t-14 t-black--light t-normal block').find_all("span")[1].text
  except:
    location = ''
  
  data = interval + ' (' + duration + ')' + location + desc
  return data

# If there is a single position/role in a particular company
def single_role(experience):
  title   = experience.find("h3", class_ = 't-16 t-black t-bold').text
  company = experience.find("p", class_ = 'pv-entity__secondary-title t-14 t-black t-normal').text.strip()
  detail  = get_detail(experience)
  
  data = company + ' ---> ' + '\n' + '- ' + title + ' \u2022 ' + detail
  return data

# If there is more than one job position in the same company
def multi_role(experience):
  all_roles = []
  company = experience.find("h3", class_ = 't-16 t-black t-bold').find_all("span")[1].text
  multi_roles = experience.find_all("li", class_ = 'pv-entity__position-group-role-item')

  for role in multi_roles:
    role_title = role.find("h3", class_ = 't-14 t-black t-bold').find_all("span")[1].text 
    detail = get_detail(role)
    role = '- ' + role_title + ' \u2022 ' + detail
    all_roles.append(role)
  all_roles = '\n\n'.join(all_roles)
  
  data = company + ' ---> ' + '\n' + all_roles
  return data
