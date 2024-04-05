from nicegui import ui

def set_notification(config, shared_softwareconfig):
    with ui.row():
        ui.link_target("NOTIFICATION")
        ui.label(config.get_text("setting_notification")).style('font-size: x-large')
    
    with ui.card():
        ui.checkbox(config.get_text("email_notification_desc")).bind_value(config.userconfigdict, 'ENABLE_MAIL_NOTI')
        ui.input(config.get_text("email_account")).bind_value(shared_softwareconfig.softwareconfigdict, "MAIL_USER").style("width: 300px")
        ui.input(config.get_text("email_pwd"), password=True).bind_value(shared_softwareconfig.softwareconfigdict, "MAIL_PASS").style("width: 300px")
        
        # 高级模式让用户自己选择邮件发送服务器
        ui.checkbox(config.get_text("config_email_advaned")).bind_value(shared_softwareconfig.softwareconfigdict, "ADVANCED_EMAIL")
        
        with ui.row().bind_visibility_from(shared_softwareconfig.softwareconfigdict, "ADVANCED_EMAIL"):
            # 发件人
            ui.input(config.get_text("config_email_sender")).bind_value(shared_softwareconfig.softwareconfigdict, "SENDER_EMAIL").style("width: 300px")
            # 收件人
            ui.input(config.get_text("config_email_receiver")).bind_value(shared_softwareconfig.softwareconfigdict, "RECEIVER_EMAIL").style("width: 300px")
            # 邮件服务器
            ui.input(config.get_text("config_email_smtp")).bind_value(shared_softwareconfig.softwareconfigdict, "MAIL_HOST").style("width: 300px")

        ui.label(config.get_text("get_email_pwd"))
        ui.html('<iframe src="//player.bilibili.com/player.html?aid=583874363&bvid=BV16z4y1D74s&cid=211611094&p=1&autoplay=0" width="720px" height="480px" scrolling="no" border="0" frameborder="no" framespacing="0" allowfullscreen="true"> </iframe>')
        