# Learn CSS by improving Andreas Moe’s site

You know HTML and a little JavaScript. This tutorial assumes **no CSS knowledge**. You’ll use your actual pages to turn a browser-default-looking site into a restrained personal site: warm background, readable text, teal links, comfortable navigation, and responsive project cards.

Allow roughly 60–90 minutes. Work through the lessons in order; each gives you something visible to check. No framework, build tool, external font, or JavaScript change is needed.

## 1. Set up a short feedback loop

From the repository root, run:

```sh
python3 -m http.server 8000
```

Open `http://localhost:8000`. Keep your editor beside the browser. Your header uses `fetch()` to load `header.html`, so use this local server instead of opening HTML files directly. Stop the server with Ctrl+C when finished.

Make a copy of `styles.css` outside the repository as a backup. Keep the existing file’s contents: we’ll **append** the lesson snippets to the bottom of it, in order. This preserves your math and demo styles while letting you see how later rules change earlier ones.

First, add this inside `<head>` in `index.html`, `projects.html`, `blog.html`, `books.html`, and `cv.html`, unless it’s already there:

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

This tells mobile browsers to use the device’s actual width for layout. Later, add it to the other full HTML pages that share your stylesheet. Don’t add it to `header.html`: that file is a fragment loaded into other pages, not a full document.

**Checkpoint:** the local homepage loads with its navigation. Take a screenshot so you can compare the result at the end.

## 2. Read your first CSS rule

HTML describes elements. CSS chooses elements and gives them visual properties:

```css
p {
    color: #26332f;
}
```

`p` is a **selector**: it matches every paragraph. Inside the braces is a **declaration**. `color` is a property; `#26332f` is its value, a hexadecimal color. The colon separates the property from its value; the semicolon ends the declaration. CSS comments use `/* comment */`.

Some selectors already used in your site:

| Selector | Matches |
| --- | --- |
| `h1` | Every `<h1>` |
| `.project-item` | Elements with `class="project-item"` |
| `#header` | The element with `id="header"` |
| `.project-item a` | Links anywhere inside a project item |

A class can label multiple elements. An ID should identify one element on a page. A space between selectors means “inside.”

Append this to `styles.css`:

```css
/* Tutorial: page foundation */
body {
    background: #f8f7f3;
    color: #26332f;
    font-family: system-ui, sans-serif;
    font-size: 1.0625rem;
    line-height: 1.7;
}
```

`background` paints the page. `font-family` asks for the operating system’s interface font, with a generic sans-serif fallback. `rem` is a unit relative to the root element’s font size: with the common 16px default, `1.0625rem` is 17px. It also respects the reader’s font preferences. Unitless `line-height: 1.7` makes each line 1.7 times the text size.

Text properties such as color and font usually **inherit**: descendants use their parent’s value unless another rule sets their own. Your existing `h1` rule sets its own font and color, so we’ll change those explicitly later.

**Try it:** change `line-height` to `1.2`, reload, then restore `1.7`. Notice how reading comfort changes without touching the HTML.

## 3. Understand the box model and page width

Every element occupies a box. From the inside out, it has **content → padding → border → margin**. Padding creates room inside the border. Margin separates the box from its neighbors.

Append:

```css
/* Include padding and borders in declared widths. */
*, *::before, *::after {
    box-sizing: border-box;
}

body {
    max-width: 72rem;
    margin: 0 auto;
    padding: 3rem 1.5rem 5rem;
}

body > p {
    max-width: 65ch;
}

img {
    max-width: 100%;
    height: auto;
}
```

`*` matches every element. `::before` and `::after` are generated boxes that CSS can create; including them makes this sizing rule consistent if you use them later.

`max-width` caps the page width but still allows it to shrink. In `margin: 0 auto`, the first value sets top/bottom margins to zero and the second splits leftover horizontal space evenly, centering the page. Three-value `padding` means top, left/right, bottom. These shortened forms are called **shorthand properties**.

`body > p` matches only paragraphs directly inside the body; `>` means “direct child.” This caps your homepage introduction at about 65 characters per line, using `ch`, the width of the font’s “0” character. Your projects can still use the wider page. It doesn’t cap every nested article paragraph; later you can give article content its own wrapper if you want a separate reading width.

The image rule lets large images shrink with their container while preserving their proportions. Your existing `.project-image` selector is more specific than `img`, so its fixed height still wins until lesson 7.

**Checkpoint:** on a wide screen the page is centered, with breathing room around it. Narrow the browser: the page should shrink without the introduction spilling sideways.

## 4. Learn the cascade while improving headings

Multiple rules can match the same element. The browser resolves them through the **cascade**. For the normal rules in your stylesheet, a more specific selector beats a less specific selector. When specificity is equal, the declaration written later wins. Rules combine property by property; a later rule doesn’t erase properties it never mentions.

For example, `.project-image` is more specific than `img`. Two `h1` rules have equal specificity, so the later one wins for any properties both set. Inheritance supplies a value only when the element has no applicable value of its own.

Append:

```css
h1, h2, h3, h4 {
    color: #183d35;
    font-family: system-ui, sans-serif;
    line-height: 1.2;
}

h1 {
    font-size: clamp(2rem, 5vw, 3.25rem);
    letter-spacing: -0.035em;
    margin: 0 0 1rem;
}

h2 {
    margin-top: 2.5rem;
}

p {
    margin: 0 0 1.25rem;
}
```

Commas group selectors that share declarations. `clamp(minimum, preferred, maximum)` makes the heading grow with the browser width while staying between two limits. `vw` means hundredths of viewport width: `5vw` is 5% of the viewport. `em` is relative to the element’s own font size here, so letter spacing scales with the heading.

**Try it:** right-click your name, choose Inspect, and find its styles. You should see the old `h1` font size crossed out. Temporarily untick the new font size in Developer Tools. These browser experiments are temporary; save permanent changes in the file.

## 5. Make links and keyboard focus intentional

Append:

```css
a {
    color: #146653;
    text-underline-offset: 0.2em;
    text-decoration-thickness: 0.08em;
}

a:hover {
    color: #0b4437;
}

a:focus-visible {
    outline: 3px solid #146653;
    outline-offset: 4px;
    border-radius: 2px;
}
```

`:hover` and `:focus-visible` are **pseudo-classes**: they match an element in a particular state. Hover responds to a pointer. Focus-visible gives keyboard users a clear marker as they Tab through links. An outline doesn’t consume layout space, so it won’t move neighboring text.

**Checkpoint:** hover over a link, then use Tab to move through the page. You should always be able to see which link has keyboard focus.

## 6. Give your existing header structure

Your `header.html` has a heading followed by links. `header.js` wraps the current page’s link in `<b>`. We can style that exact structure without changing the script.

Append:

```css
#header {
    margin-bottom: 2.5rem;
    padding-bottom: 1.25rem;
    border-bottom: 1px solid #d7ded7;
}

#header h1 a {
    color: inherit;
    text-decoration: none;
}

#header a:not(#index) {
    display: inline-block;
    margin: 0.25rem 0.65rem 0.25rem 0;
    padding: 0.25rem 0;
}

#header b > a {
    text-decoration-thickness: 0.16em;
}

#header hr {
    display: none;
}
```

`inherit` explicitly takes the parent’s color. `:not(#index)` excludes the link containing your name. `inline-block` lets links sit next to one another while accepting box spacing; they wrap when the row fills up. Four margin values mean top, right, bottom, left, clockwise.

We hide the old horizontal rule because the header now draws its own bottom border. The current page’s navigation underline becomes thicker. Since the name link deliberately has no underline, this current-page treatment is visible on the other navigation links.

**Checkpoint:** visit the Blog and Projects pages and check their active links. Narrow the browser and confirm the navigation wraps comfortably.

## 7. Replace fixed-width project cards with a grid

Your `.project-list` currently uses flexbox with 300px-wide cards. Flexbox is useful for arranging items along a row or column. Here we’ll use **Grid**, which lays items out in rows and columns and can calculate how many columns fit.

Append:

```css
.project-list {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(min(100%, 18rem), 1fr));
    gap: 1.5rem;
    padding: 0;
}

.project-item {
    width: auto;
    background: #fff;
    border: 1px solid #d7ded7;
    border-radius: 0.75rem;
    box-shadow: 0 3px 12px rgb(24 61 53 / 6%);
}

.project-link {
    height: 100%;
}

.project-image {
    height: auto;
    aspect-ratio: 3 / 2;
    object-fit: cover;
}

.project-title {
    margin: 0;
    padding: 1.25rem;
    color: #183d35;
    font-size: 1.15rem;
}

.project-item:hover,
.project-item:focus-within {
    border-color: #146653;
}

.project-link:focus-visible {
    outline-offset: -4px;
}
```

Read the long grid declaration from the inside out:

1. `min(100%, 18rem)` chooses the smaller of the container width and 18rem, so a column can fit a narrow phone.
2. `minmax(..., 1fr)` lets a column grow from that minimum and take a share of the available space. `fr` means a fraction of leftover grid space.
3. `repeat(auto-fit, ...)` creates as many of those columns as fit.

`width: auto` overrides the old 300px width so the grid controls card sizing. `aspect-ratio` gives images consistent proportions; `object-fit: cover` fills the image box by cropping edges when necessary. Your old `overflow: hidden` still applies to cards, clipping images to the rounded corners. The inward link outline keeps keyboard focus visible inside those clipped cards. `:focus-within` matches a card when its link has focus.

**Try it:** change `18rem` to `22rem`. Predict whether you’ll get more or fewer columns before you reload. Restore whichever size you prefer.

**Checkpoint:** Projects should move from several columns to one as you narrow the window. Some project images contain diagrams: check that the cropping is acceptable. If you need the whole diagram visible, change `object-fit: cover` to `contain`; this can leave unused space around it. CSS won’t fix an image that fails to download.

## 8. Make the finishing adjustments for phones

A **media query** applies rules only when a condition matches. Append:

```css
@media (max-width: 40rem) {
    body {
        padding: 1.5rem 1rem 3rem;
    }

    #header {
        margin-bottom: 2rem;
    }

    .lefttext {
        min-width: 0;
        flex-basis: 100%;
    }

    .rightdemo {
        min-width: 0;
        flex-basis: 100%;
    }
}
```

Below 40rem, the outer spacing gets smaller. Your existing `.textanddemo` uses a wrapping flex layout. `flex-basis: 100%` makes its text and demo children each request a full row on small screens. Removing the existing 300px text minimum lets the text fit even when the available space is smaller.

**Checkpoint:** check the homepage and Projects at 375px in your browser’s responsive mode. Also inspect an interactive article such as `rlhf.html`. Widgets and inline styles may need their own adjustments; a shared stylesheet can’t guarantee every embedded demo fits.

## 9. Finish, verify, and make it yours

Compare your initial screenshot with the current homepage. You’ve changed page composition, reading rhythm, visual hierarchy, navigation, and the project layout using CSS alone, plus the mobile viewport metadata.

Before calling it finished:

- Check Home, Blog, Projects, Books, and CV at desktop and phone widths.
- Tab through links and confirm focus stays visible, especially on project cards.
- Zoom to 200% and check that navigation and content remain usable.
- Check a long technical article with code, tables, math, and images. Wide tables or fixed-size widgets may need a separate improvement.
- Add the viewport metadata to the remaining full pages using `styles.css`.

**Final exercise:** choose one change: a different link color, a slightly narrower page, or larger card spacing. Find the declaration responsible, predict its effect, then edit and reload. Change one variable at a time so you learn what it controls.

You can keep the appended rules while learning. Once comfortable, move each final declaration into its original matching rule and remove superseded declarations. Keep the specialized math, table, and demo rules. Repeat your visual checks after this cleanup: rearranging selectors can change which rule wins.

To undo the tutorial changes, restore your backup of `styles.css` and remove the viewport lines you added. The tutorial itself doesn’t change your live pages; you make each improvement as you learn it.
