document.addEventListener('DOMContentLoaded', function() {
    const editors = document.querySelectorAll('.rich-text-editor');
    
    editors.forEach(editor => {
        const toolbar = document.createElement('div');
        toolbar.className = 'editor-toolbar';
        toolbar.innerHTML = `
            <button type="button" data-command="bold" title="Bold"><b>B</b></button>
            <button type="button" data-command="italic" title="Italic"><i>I</i></button>
            <button type="button" data-command="underline" title="Underline"><u>U</u></button>
            <button type="button" data-command="insertOrderedList" title="Numbered List">1.</button>
            <button type="button" data-command="insertUnorderedList" title="Bullet List">•</button>
            <button type="button" data-command="createLink" title="Insert Link">🔗</button>
            <button type="button" data-command="code" title="Code Block">{ }</button>
        `;

        editor.parentNode.insertBefore(toolbar, editor);

        toolbar.querySelectorAll('button').forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                const command = this.dataset.command;

                if (command === 'createLink') {
                    const url = prompt('Enter the URL:');
                    if (url) {
                        const selectedText = window.getSelection().toString();
                        const linkText = selectedText || url;
                        const link = `[${linkText}](${url})`;
                        insertTextAtCursor(editor, link);
                    }
                } else if (command === 'code') {
                    const selectedText = window.getSelection().toString();
                    const codeBlock = selectedText ? 
                        '```\n' + selectedText + '\n```' :
                        '```\n\n```';
                    insertTextAtCursor(editor, codeBlock);
                } else {
                    const selectedText = window.getSelection().toString();
                    let formattedText = '';
                    
                    switch(command) {
                        case 'bold':
                            formattedText = `**${selectedText}**`;
                            break;
                        case 'italic':
                            formattedText = `*${selectedText}*`;
                            break;
                        case 'underline':
                            formattedText = `_${selectedText}_`;
                            break;
                        case 'insertOrderedList':
                            formattedText = `\n1. ${selectedText}`;
                            break;
                        case 'insertUnorderedList':
                            formattedText = `\n- ${selectedText}`;
                            break;
                    }
                    
                    if (formattedText) {
                        insertTextAtCursor(editor, formattedText);
                    }
                }
            });
        });
    });
});

function insertTextAtCursor(textarea, text) {
    const startPos = textarea.selectionStart;
    const endPos = textarea.selectionEnd;
    const scrollTop = textarea.scrollTop;

    textarea.value = textarea.value.substring(0, startPos) + 
                    text + 
                    textarea.value.substring(endPos, textarea.value.length);
    
    textarea.focus();
    textarea.selectionStart = startPos + text.length;
    textarea.selectionEnd = startPos + text.length;
    textarea.scrollTop = scrollTop;
}