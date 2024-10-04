# The UPL Programming Language

New programming language I'm making

# How to use

``` UPL
# This is a comment

var name = "value"

var num1 = 5
var num2 = 7

function.create demoFunc() {
	!println("This is a function")
}

!println("Prints something with a newline")
!print("Prints something without a newline")
!expyth(" print('This lets you execute python code!') ")

demoFunc()

if (num1 < num2) {
	!println("This condition is true!")
}
```

Output:
```
Prints something with a newline
Prints something without a newlineThis lets you execute python code!
This is a function
This condition is true!
```