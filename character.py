class Character:
  def __init__(self, name, realm='stormrage', locale='us'):
    self.name_ = name
    self.realm_ = realm
    self.locale_ = locale

  @property
  def name(self):
    return self.name_

  @property
  def realm(self):
    return self.realm_

  @property
  def locale(self):
    return self.locale_
