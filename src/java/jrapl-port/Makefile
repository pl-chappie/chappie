all: jrapl

jrapl:
	mkdir classes
	make -C src/jrapl all
	javac -d classes src/jrapl/*.java
	cp src/jrapl/*.so classes/jrapl
	cp src/jrapl/*.so classes
	cp src/jrapl/*.h classes

clean:
	make -C src/jrapl clean
	rm -rf classes
