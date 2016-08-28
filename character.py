class Character:
  def __init__(self, name, realm='stormrage', locale='us', talents=None):
    self.name_ = name
    self.realm_ = realm
    self.locale_ = locale
    self.talents_ = talents

  @property
  def name(self):
    return self.name_

  @property
  def realm(self):
    return self.realm_

  @property
  def locale(self):
    return self.locale_

  @property
  def talents(self):
    return self.talents_

  def DebugString(self):
    return "{}-{}-{}{}".format(
      self.name_, self.realm_, self.locale_,
      "-" + self.talents_ if self.talents_ is not None else '')

  def ArmoryFileName(self):
    return "{}-{}-{}.simc".format(
      self.name_, self.realm_, self.locale_)
