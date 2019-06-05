# Specify which Beaker RPM package will be generated - devel o production?
DEVEL := yes

# The toplevel namespace within which the test lives.
TOPLEVEL_NAMESPACE=/performance

# Include Common Makefile
include /usr/share/rhts/lib/rhts-make.include

# Include Makefile.dist for making beaker independent rpms
include Makefile.dist

# Version of the Test. Used with make tag.
export TESTVERSION=$(VERSION)

# The compiled namespace of the test.
export TEST=$(TOPLEVEL_NAMESPACE)/$(PACKAGE_NAME)

.PHONY: all install download clean

clean: rpms-clean
	find . -type f -name "*.pyc" -exec rm -f {} \;

FILES=$(METADATA)  \
		Makefile\
		Makefile.dist\
		README.md\
		sync_client\
		synchronization\
		sync_server\
		runtest.sh\
		synchronization.service\
		setup.py

build: $(BUILT_FILES)
		chmod a+x ./setup.py
		chmod a+x ./sync_client
		chmod a+x ./sync_server
		chmod a+x ./runtest.sh

run: $(FILES) build
		./runtest.sh

# Generate the testinfo.desc here:
$(METADATA): Makefile
	@touch $(METADATA)
	@echo "Owner:        Adam Okuliar <aokuliar@redhat.com>" > $(METADATA)
	@echo "Name:         $(TEST)" >> $(METADATA)
	@echo "Path:         $(TEST_DIR)"	>> $(METADATA)
	@echo "TestVersion:  $(TESTVERSION)"	>> $(METADATA)
	@echo "Description:  Synchronization for Beaker tasks.">> $(METADATA)
	@echo "TestTime:     3h" >> $(METADATA)
	@echo "RunFor:       $(PACKAGE_NAME)" >> $(METADATA)
	@echo "Requires:     $(PACKAGE_NAME)" >> $(METADATA)
	@echo "Releases:      -RHEL5.5" >> $(METADATA)
	@echo "Architectures: x86_64" >> $(METADATA)
	@echo "Confidential:  no" >> $(METADATA)
	@echo "Priority:      Normal" >> $(METADATA)
	@echo "Type:          Certification" >> $(METADATA)
	@echo "RunFor:        none" >> $(METADATA)
	@echo "License:       NDA" >> $(METADATA)

SPECIAL_MAKEFILE=Makefile.production
ifeq ($(DEVEL), yes)
        SPECIAL_MAKEFILE=Makefile.devel
endif
include $(SPECIAL_MAKEFILE)

