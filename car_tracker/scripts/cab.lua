function main(splash, args)
splash.private_mode_enabled = false
assert(splash:go(args.url))
assert(splash:wait(10))
splash:set_viewport_full()
splash:runjs("window.scrollTo(0, document.body.scrollHeight)")
assert(splash:wait(2))
assert(splash:go(args.url))
assert(splash:wait(0.5))
return {
html = splash:html(),
png = splash:png(),
har = splash:har(),
}
end