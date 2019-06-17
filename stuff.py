from pprint import pprint
import hotload

def sayhello(msg):
    print("Hello, {}, hope you'll have a nice day!".format(msg))

# hotload.hotload(**runconf)
# hotload.hotload(watch=["*"], steps=[1, 2])
hotload.hotload_single_iter(
    watch=["*"],
    steps=[
        hotload.ClearTerminal(),
        hotload.Command("echo Hello from step 1"),
        hotload.PythonHandle(lambda: sayhello("Cakemaster")),
        hotload.PythonModule.from_module_name("myscript"),
    ]
)
