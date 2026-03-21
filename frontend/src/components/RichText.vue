<template>
    <span v-html="rendered"></span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
    text: { type: String, default: '' }
})

const rendered = computed(() => {
    if (!props.text) return ''

    return props.text
        // Gras : **texte** → <strong>texte</strong>
        // Important : traiter le gras AVANT l'italique
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        // Italique : *texte* → <em>texte</em>
        .replace(/\*(.+?)\*/g, '<em>$1</em>')
        // Sauts de ligne
        .replace(/\n/g, '<br>')
})
</script>