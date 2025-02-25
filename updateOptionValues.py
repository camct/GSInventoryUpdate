from inventoryTrack import ecwidCall
from maintainDefault import DefaultUpdater

if __name__=='__main__':
    token = ''
    inventory_manager = ecwidCall()
    inventory_manager.token = token
    inventory_manager.updateOptionValues()
    default_updater = DefaultUpdater()
    default_updater.token = token
    default_updater.updateDefaultStrap()