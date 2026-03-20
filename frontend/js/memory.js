// Memory Management
const MemoryManager = {
    async getMemories() {
        try {
            const data = await APIManager.get('/memory');
            return data || [];
        } catch (error) {
            console.error('Error fetching memories:', error);
            return [];
        }
    },

    async storeMemory(key, value) {
        try {
            await APIManager.post('/memory', { key, value });
            NotificationManager.success('Memory saved');
        } catch (error) {
            console.error('Error storing memory:', error);
            NotificationManager.error('Failed to save memory');
        }
    },

    async updateMemory(key, value) {
        try {
            await APIManager.put('/memory', { key, value });
            NotificationManager.success('Memory updated');
        } catch (error) {
            console.error('Error updating memory:', error);
            NotificationManager.error('Failed to update memory');
        }
    },

    async deleteMemory(key) {
        try {
            await APIManager.delete('/memory', { key });
            NotificationManager.success('Memory deleted');
        } catch (error) {
            console.error('Error deleting memory:', error);
            NotificationManager.error('Failed to delete memory');
        }
    },

    async searchMemories(query) {
        try {
            const memories = await this.getMemories();
            return memories.filter(mem =>
                mem.key.toLowerCase().includes(query.toLowerCase()) ||
                mem.value.toLowerCase().includes(query.toLowerCase())
            );
        } catch (error) {
            console.error('Error searching memories:', error);
            return [];
        }
    },

    async getMemoryByKey(key) {
        try {
            const memories = await this.getMemories();
            return memories.find(mem => mem.key === key);
        } catch (error) {
            console.error('Error fetching memory:', error);
            return null;
        }
    }
};

// Export for use in other scripts
window.MemoryManager = MemoryManager;
