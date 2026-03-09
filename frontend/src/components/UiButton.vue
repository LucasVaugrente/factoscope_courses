<template>
  <button :class="variant" :disabled="disabled">
    <slot />
  </button>
</template>

<script setup>
defineProps({
  variant: { type: String, default: 'primary' }, // primary | ghost
  disabled: { type: Boolean, default: false }
})
</script>

<style scoped>
.primary {
  background: #667eea;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 10px 16px;
  min-height: 40px;
  line-height: 1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-weight: 600;
}
.ghost {
  background: transparent;
  color: #667eea;
  border: 1px solid #d8ddff;
  border-radius: 8px;
  padding: 10px 14px;
  cursor: pointer;
  font-weight: 600;
}
button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}
</style>
