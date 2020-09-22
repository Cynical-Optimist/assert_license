# License information in BuildStream public data, & the `assert_license` plugin

## Proposal

1) Create a standard for recording license information as part of a BuildStream
element's public data.

This information would be added by hand (not automatically) after a human being
had reviewed the relevant licenses for the element. It could be added when the
element is first created, or added later during a review process. It would
presumably need to be updated if and when relevant license information changed.

For example, if we added license information about python3, to the python3.bst
file from freedesktop-sdk:
```
kind: autotools
description: Python 3

public:
  licenses:
    license-strings:
    - foo license 1
    - bar license (2.0)
    - baz license WITH particular exception
    - foo-bar license OR bar-foo license

build-depends:
- components/bluez-headers.bst
- public-stacks/buildsystem-autotools.bst
...
...
```

A tool like licensecheck or scancode can be helpful in
identifying licenses (perhaps assisted by a wrapper script like
`buildstream_license_checker`) but the final task of recording the licenses 
should still involve a human review.


2) Create an `assert_license` plugin, which consumes this public data

The `assert_license` plugin would read the public data from its dependencies and
recursive dependencies. It could collate this data into a summary output, but
the main goal would be that users can specify a license blacklist in the element
configuration.

If any licenses are detected which violate the blacklist, the element will fail
to build, and produce a useful error message in the log. This would directly
prevent a project from building if it has blacklisted licenses.

For example:

```
kind: `assert_license`

build-depends:
- file-a.bst
- file-b.bst

config:
  dependency_scope: ALL
  blacklist:
    - foo license 1
    - foo license version 2
```

Of course, the `assert_license` plugin is only one example of how downstream
elements might consume the license public data. Once the information is made
available in the public data, people could write or adapt other plugins to make
use of it in different ways.


## Assumptions

This approach makes a lot of assumptions:

#### Public data

To get people recording license information in public data, we have to assume:
* Element creators know about (and are interested in) the licenses that
  apply to their elements.
* Element creators want to (or are willing to) report the license information,
  and to record it in the license declarations
* The information reported will be accurate and up to date enough to be useful

I'm told this is common in Business scenarios, but I haven't witnessed it in any
of the open source projects that I've worked on.

#### `assert_license` plugin

To get people using the `assert_license` plugin, we have to assume:
* People want to know license information about the elements they consume
* License declarations will actually be available in the public data of
  elements.
* The License declarations will be useful, because:
  * EITHER: users will trust that the license declarations are complete and
    accurate enough to use, without performing their own investigations of the
    source code.
  * OR: users *will* perform their own investigations of the source code, but
    the will somehow still find the license declarations useful anyway.

The last point is crucial. License information in public data is really only
useful to the extent that you're willing to trust its accuracy. It isn't
validated by any automated process (and couldn't realistically be automated).
It's a claim made by one human being, to others. If you don't trust the public
data to be accurate, then you will probably disregarded it and investigate the
source code yourself.

This suggests that public-data license information might be most useful when
it's used internally, ie within a project. If an organisation controls a
project, then they can trust the data that they put into it.

#### Other assumptions

For the blacklisting process to work, `assert_license` has to be able to
recocognize black-listed licenses when it sees them. This means assuming:
* The same license will always be recorded in the same way, ie with the exact
  same text string
* OR it will be possible somehow for the algorithm to recocognize when two
  different text strings are describing the same license.


## Use cases

In the simplest possible license-checking scenario, a user wants to do a
one-time investigation of an existing project. They inspect the entire project,
collect a list of licenses, and check for blacklist violations. That scenario
would *NOT* be a good use case for the approach laid out here. In that scenario,
there would be no point in separating out the license information into so many
different files before bringing it back together again.

So when is this approach useful?

#### Maintaining one project, over time

Projects change over time, as elements are added, modified, and deleted. If
users are interested in license information, they will likely want more than a
single snapshot of the license data. They will want to keep license data up to
date as the project changes.

Storing license information inside the element declarations (the .bst files),
has a number of benefits:

* At a glance, you can see the license information for any given element (or see
  that it is missing).
* This encourages people to add license information to an element whenever it's
  created (if that becomes the standard policy on a project).
* License information gets automatically removed when the element is removed.

#### Multiple outputs, with different dependencies

A project may produce multiple different 'outputs', (eg producing the
software in different formats, or for different platforms, or producing it with
and without extensions). These will usually not have identical dependencies, so
they may not have identical license lists. By tracing an element's dependency
tree, you can automatically collect the license information for the correct set
of dependency elements without having to cross-reference anything.

#### Junctioned elements

A downstream project may want to consume your elements through a junction, and
they could pick any subset of elements to consume. If you store license
information directly in the element declarations, then downstream projects will
inherit the license information for the exact set of elements that they consume,
no more, no less. They'll also inherit the information automatically, just by
junctioning the element.

(However, as stated above, this is only useful to the extent that downstream is
willing to trust your license information.)


## Unanswered Questions
#### Basics
* Who actually wants this functionality?
* Who would use it?
* Do people know enough about licenses to fill this information in accurately?
* Are people confident enough about licenses to fill this information in?

#### Format
* How does a consistent format get enforced? (So that blacklist entries can be
  matched to license-string entries.)

#### Specificity
* Should an element only store license information about its own artifact? (ie
  the artifact you get with a "--deps none" checkout.), and never include
  license information about its dependencies?
* What do you do if you import an upstream element, which doesn't have any
  license public data?
  * Specifically, if you manage to find out the correct license information for
    the junctioned element, can you insert the information somehow into your own
    project?

#### Filters and Compose elements
* What do we do with a filter element or a compose element?
  * A filter or compose element can remove files from artifacts. Licenses which
    applied to the complete artifact may not all apply to the reduced artifact.
    Can we account for this somehow?
